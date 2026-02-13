from aiogram import F, Router, flags
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.db.models import Window
from django.db.models.functions import RowNumber

from bot.callback_data import IntDetailActionCallback
from bot.filters import action_filter
from bot.keyboards.matching import start_matching_kb
from bot.keyboards.registration import (
    get_answers_kb,
    get_career_focus_directions_kb,
    get_career_focuses_kb,
    get_cities_kb,
    get_departments_kb,
    get_genders_kb,
    get_interests_kb,
    get_lifestyles_kb,
    get_yes_no_kb,
)
from bot.loader import logger
from bot.services.matching import find_match
from bot.states import RegistrationState
from bot.texts import (
    career_focus_bot_answers,
    career_focuses_text,
    lifestyles_bot_answers,
)
from bot.types import expect
from core.choices import Lifestyle, QuestionKey, Territory
from core.models import (
    CareerFocusDirection,
    City,
    Department,
    Interest,
    Match,
    Profile,
    ProfileAnswer,
    ProfileInterest,
    ProfileLifestyle,
    Question,
    User,
)

router = Router()


@router.message(Command('start'))
async def start_handler(msg: Message, state: FSMContext) -> None:
    user, created = await User.objects.create_or_update(expect(msg.from_user))

    if created:
        logger.info(f'New user {user} id={user.pk} was created')
    else:
        logger.info(f'User {user} id={user.pk} was updated')

    if await Profile.objects.filter(user=user).aexists():
        await msg.answer(f'Привет, {msg.from_user.full_name}!')
        return

    await state.clear()
    await msg.answer(
        'Добро пожаловать в Дикообщительный бот!\n\n'
        'Здесь мы не ищем «идеального коллегу».\n'
        'Мы ищем людей, с которыми хочется:\n'
        ' — общаться\n'
        ' — развиваться\n'
        ' — работать в удовольствие\n'
        'Ответь на вопросы анкеты — '
        'и бот подберет для тебя идеального собеседника!\n',
        reply_markup=start_matching_kb,
    )


@router.callback_query(F.data == 'start_matching')
async def start_matching_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(RegistrationState.name)
    await query.message.edit_text(
        'Напиши имя или ник, его будут видеть пользователи, '
        'с которыми будет мэтч',
    )


@router.message(F.text, StateFilter(RegistrationState.name))
async def set_name_handler(msg: Message, state: FSMContext) -> None:
    await state.update_data(name=msg.text)
    await state.set_state(RegistrationState.gender)
    await msg.answer('Твой пол', reply_markup=get_genders_kb())


@router.callback_query(
    F.data.startswith('gender'),
    StateFilter(RegistrationState.gender),
)
async def set_gender_handler(query: CallbackQuery, state: FSMContext) -> None:
    gender = query.data.split(':')[1]
    await state.update_data(gender=gender)
    await state.set_state(RegistrationState.city)
    await query.message.edit_text(
        'Принял. Учту в формулировках и комплиментах.\n\n'
        'Откуда ты? Выбери город или напиши свой',
        reply_markup=await get_cities_kb(),
    )


async def _get_departments_text() -> str:
    return '\n'.join(
        [
            f'{d.number}. {d}'
            async for d in Department.objects.annotate(
                number=Window(expression=RowNumber(), order_by='id'),
            ).all()
        ],
    )


@router.callback_query(
    action_filter('city', 'select', detail=True),
    StateFilter(RegistrationState.city),
)
async def set_city_query_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: IntDetailActionCallback,
) -> None:
    city = await City.objects.aget(pk=callback_data.pk)
    await state.update_data(city_id=city.pk)
    await state.set_state(RegistrationState.department)
    departments_text = await _get_departments_text()
    await query.message.edit_text(
        'География важна. Иногда мэтч начинается с «пойдём за кофе».\n\n'
        f'Из какого ты департамента?\n\n{departments_text}',
        reply_markup=await get_departments_kb(),
    )


@router.message(F.text, StateFilter(RegistrationState.city))
async def set_city_message_handler(msg: Message, state: FSMContext) -> None:
    city, _ = await City.objects.aget_or_create(name=msg.text)
    await state.update_data(city_id=city.pk)
    await state.set_state(RegistrationState.department)
    departments_text = await _get_departments_text()
    await msg.answer(
        'География важна. Иногда мэтч начинается с «пойдём за кофе».\n\n'
        f'Из какого ты департамента?\n\n{departments_text}',
        reply_markup=await get_departments_kb(),
    )


@router.callback_query(
    action_filter('department', 'select', detail=True),
    StateFilter(RegistrationState.department),
)
async def set_department_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: IntDetailActionCallback,
) -> None:
    department = await Department.objects.aget(pk=callback_data.pk)
    question_key = QuestionKey.EVENING_MOVIE
    question = await Question.objects.prefetch_related('answers').aget(
        key=question_key,
    )

    answer = question.answers.all()[0]
    yes_no_answers_ids = [a.pk for a in question.answers.all()]
    yes_no_answers_ids.pop(0)

    await state.update_data(
        department_id=department.pk,
        questions_ids=await Question.objects.get_ids_for_keys([question_key]),
        current_question_index=0,
        next_question_function_key='ask_lifestyle',
        current_answer_id=answer.pk,
        current_yes_no_answers_ids=yes_no_answers_ids,
    )

    await state.set_state(RegistrationState.questions)
    await query.message.edit_text(
        f'Отлично. Значит, возможны совпадения прямо за соседним столом.\n\n'
        f'{question.text}\n\n{answer.text}',
        reply_markup=get_yes_no_kb(),
    )


@router.callback_query(
    F.data.startswith('lifestyle'),
    StateFilter(RegistrationState.lifestyle),
)
async def set_lifestyle_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    lifestyle = query.data.split(':')[1]
    data = await state.get_data()
    lifestyles = data.get('lifestyles', [])

    if not lifestyles:
        data['lifestyles_base_text'] = query.message.text

    if lifestyle == 'done':
        if not lifestyles:
            await query.answer('Надо выбрать хотя бы одно', show_alert=True)
            return

        territories = list(Territory.values)
        first_territory = territories.pop(0)
        await state.update_data(
            territories=territories,
            current_territory=first_territory,
        )
        await state.set_state(RegistrationState.interest)
        answer_text = lifestyles_bot_answers.get(frozenset(lifestyles))
        await query.message.edit_text(
            f'{answer_text}\n\n'
            f'{Territory(first_territory).label}\n'
            f'Что из этого тебе ближе?',
            reply_markup=await get_interests_kb(first_territory),
        )
        return

    if lifestyle in lifestyles:
        lifestyles.remove(lifestyle)
    else:
        lifestyles.append(lifestyle)

    await state.set_data({**data, **{'lifestyles': lifestyles}})
    await query.message.edit_text(
        f'{data["lifestyles_base_text"]}\n\n'
        f'Вы выбрали: {", ".join([Lifestyle(i).label for i in lifestyles])}',
        reply_markup=get_lifestyles_kb(),
    )


@router.callback_query(
    action_filter('interest', 'select', detail=True),
    StateFilter(RegistrationState.interest),
)
async def set_interest_query_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: IntDetailActionCallback,
) -> None:
    data = await state.get_data()
    current_territory = data['current_territory']
    interests_ids = data.get('interests_ids', [])

    interest = await Interest.objects.aget(pk=callback_data.pk)
    if interest.pk in interests_ids:
        interests_ids.remove(interest.pk)
    else:
        interests_ids.append(interest.pk)
    data['interests_ids'] = interests_ids

    interests_text = '\n'.join(
        [
            str(i)
            async for i in Interest.objects.filter(
                pk__in=interests_ids,
                territory=current_territory,
            )
        ],
    )

    await state.set_data(data)
    await query.message.edit_text(
        f'{Territory(current_territory).label}\n'
        f'Что из этого тебе ближе?\n\n'
        f'Ты выбрал:\n{interests_text}',
        reply_markup=await get_interests_kb(current_territory),
    )


@router.callback_query(F.data == 'interest:done')
async def interest_done_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    territories = data['territories']

    if not territories:
        await state.set_state(RegistrationState.career_focus)
        await query.message.edit_text(
            career_focuses_text,
            reply_markup=get_career_focuses_kb(),
        )
        return

    territory = territories.pop(0)
    data['territories'] = territories
    data['current_territory'] = territory
    await state.set_data(data)
    await query.message.edit_text(
        f'{Territory(territory).label}\nЧто из этого тебе ближе?\n\n',
        reply_markup=await get_interests_kb(territory),
    )


@router.message(F.text, StateFilter(RegistrationState.interest))
async def set_interest_message_handler(
    msg: Message,
    state: FSMContext,
) -> None:
    interest, _ = await Interest.objects.aget_or_create(name=msg.text)
    data = await state.get_data()
    interests_ids = data.get('interests_ids', [])
    interests_ids.append(interest.pk)
    await msg.answer(
        f'"{interest}" добавлено\n\n'
        f'Нажми готово, чтобы перейти к следующему шагу',
    )


@router.callback_query(
    F.data.startswith('career_focus'),
    StateFilter(RegistrationState.career_focus),
)
async def set_career_focus_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    career_focus = query.data.split(':')[1]
    await state.update_data(career_focus=career_focus)
    await state.set_state(RegistrationState.career_focus_direction)
    answer_text = career_focus_bot_answers[career_focus]
    await query.message.edit_text(
        answer_text,
        reply_markup=await get_career_focus_directions_kb(career_focus),
    )


@router.callback_query(
    action_filter('career_focus_direction', 'select', detail=True),
    StateFilter(RegistrationState.career_focus_direction),
)
async def set_career_focus_direction_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: IntDetailActionCallback,
) -> None:
    career_focus_direction = await CareerFocusDirection.objects.aget(
        pk=callback_data.pk,
    )

    questions_ids = await Question.objects.get_ids_for_keys(
        [
            QuestionKey.SHARE_SKILL_CARD,
            QuestionKey.MONEY_HABITS,
            QuestionKey.COMPANY_ROLE,
            QuestionKey.WHY_FUN_TO_BE_WITH,
            QuestionKey.INTERESTING_TO_TALK_WITH,
            QuestionKey.WHY_HERE,
        ],
    )
    question = await Question.objects.prefetch_related('answers').aget(
        pk=questions_ids[0],
    )

    answer = question.answers.all()[0]
    yes_no_answers_ids = [a.pk for a in question.answers.all()]
    yes_no_answers_ids.pop(0)

    await state.update_data(
        career_focus_direction_id=career_focus_direction.pk,
        questions_ids=questions_ids,
        current_question_index=0,
        next_question_function_key='ask_search_type',
        current_answer_id=answer.pk,
        current_yes_no_answers_ids=yes_no_answers_ids,
    )
    await state.set_state(RegistrationState.questions)
    await query.message.edit_text(
        f'{question.text}\n\n{answer.text}',
        reply_markup=get_yes_no_kb(),
    )


@router.callback_query(
    F.data.startswith('search_type'),
    StateFilter(RegistrationState.search_type),
)
async def set_search_type_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    search_type = query.data.split(':')[1]
    question_key = QuestionKey.COMMUNICATION_STYLE
    await state.update_data(
        search_type=search_type,
        questions_ids=await Question.objects.get_ids_for_keys([question_key]),
        current_question_index=0,
        next_question_function_key='ask_workday_type',
    )
    await state.set_state(RegistrationState.questions)
    question = await Question.objects.prefetch_related('answers').aget(
        key=question_key,
    )
    await query.message.edit_text(
        f'Хм, интересный запрос. Записываю приоритеты.\n\n{question.text}',
        reply_markup=get_answers_kb(question.answers.all()),
    )


@router.callback_query(
    F.data.startswith('workday_type'),
    StateFilter(RegistrationState.workday_type),
)
@flags.user
async def set_workday_type_handler(
    query: CallbackQuery,
    state: FSMContext,
    user: User,
) -> None:
    workday_type = query.data.split(':')[1]
    data = await state.get_data()

    profile = await Profile.objects.acreate(
        user=user,
        name=data['name'],
        gender=data['gender'],
        city_id=data['city_id'],
        department_id=data['department_id'],
        career_focus_direction_id=data['career_focus_direction_id'],
        search_type=data['search_type'],
        workday_type=workday_type,
    )
    await ProfileLifestyle.objects.abulk_create(
        [
            ProfileLifestyle(profile=profile, lifestyle=lifestyle)
            for lifestyle in data['lifestyles']
        ],
        ignore_conflicts=True,
    )
    await ProfileInterest.objects.abulk_create(
        [
            ProfileInterest(profile=profile, interest_id=interest)
            for interest in data['interests_ids']
        ],
        ignore_conflicts=True,
    )
    await ProfileAnswer.objects.abulk_create(
        [
            ProfileAnswer(profile=profile, answer_id=answer_id)
            for answer_id in data['answers_ids']
        ],
        ignore_conflicts=True,
    )

    matched_user = await find_match(user)
    if not matched_user:
        await query.message.edit_text(
            'Готово! Твой профиль в игре.\n\n'
            'Теперь моя очередь: '
            'ищу собеседника, который разделит твои идеи и зарядит энергией. '
            'Мы ценим твой подход — '
            'подбор будет максимально точным под твои цели.\n\n'
            'На связи! Скоро пришлю твою первую рекомендацию для знакомства',
        )
        return

    initiator_topic = await query.bot.create_forum_topic(
        query.message.chat.id,
        name=matched_user.profile.name,
    )
    recipient_topic = await query.bot.create_forum_topic(
        matched_user.id,
        name=user.profile.name,
    )
    await Match.objects.acreate(
        initiator=user,
        initiator_thread_id=initiator_topic.message_thread_id,
        recipient=matched_user,
        recipient_thread_id=recipient_topic.message_thread_id,
    )

    await state.clear()
    await query.message.edit_text(
        'Готово! Твой профиль в игре.\n\n'
        'Нашел собеседника, который разделит твои идеи и зарядит энергией. '
        'Ты можешь отправить ему сообщение через тему.',
    )
