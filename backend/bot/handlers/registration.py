from aiogram import F, Router, flags
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

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
    get_match_types_kb,
    get_search_types_kb,
    get_territories_kb,
    get_workday_types_kb,
)
from bot.loader import logger
from bot.services.matching import find_match
from bot.states import RegistrationState
from bot.texts import (
    career_focus_bot_answers,
    career_focuses_text,
    lifestyles_bot_answers,
    territories_text,
    territory_bot_answers,
)
from bot.types import expect
from core.choices import Lifestyle
from core.models import (
    Answer,
    CareerFocusDirection,
    City,
    Department,
    Interest,
    Match,
    Profile,
    ProfileLifestyle,
    Question,
    User,
    UserAnswer,
)

router = Router()


@router.message(Command('start'))
async def start_handler(msg: Message, state: FSMContext) -> None:
    user, created = await User.objects.create_or_update(expect(msg.from_user))

    if created:
        logger.info(f'New user {user} id={user.pk} was created')
    else:
        logger.info(f'User {user} id={user.pk} was updated')

    if hasattr(user, 'profile_id'):
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
        'Напишите ваше имя или ник. '
        'Его будут видеть пользователи, с которыми у Вас будет мэтч',
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
    await query.message.edit_text(
        'География важна. Иногда мэтч начинается с «пойдём за кофе».\n\n'
        'Из какого ты департамента?',
        reply_markup=await get_departments_kb(),
    )


@router.message(F.text, StateFilter(RegistrationState.city))
async def set_city_message_handler(msg: Message, state: FSMContext) -> None:
    city, _ = await City.objects.aget_or_create(name=msg.text)
    await state.update_data(city_id=city.pk)
    await state.set_state(RegistrationState.department)
    await msg.answer(
        'География важна. Иногда мэтч начинается с «пойдём за кофе».\n\n'
        'Из какого ты департамента?',
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
    question_key = 'evening_movie'
    await state.update_data(
        department_id=department.pk,
        questions_ids=[
            i
            async for i in Question.objects.filter(
                key=question_key,
            ).values_list('pk', flat=True)
        ],
        next_question_function_key='ask_lifestyle',
    )
    await state.set_state(RegistrationState.questions)
    question = await Question.objects.prefetch_related('answers').aget(
        key=question_key,
    )
    await query.message.edit_text(
        f'Отлично. Значит, возможны совпадения прямо за соседним столом.\n\n'
        f'{question.text}',
        reply_markup=get_answers_kb(question.answers.all()),
    )


# @router.callback_query(
#     F.data.startswith('evening_movie'),
#     StateFilter(RegistrationState.evening_movie),
# )
# async def set_evening_movie_handler(
#     query: CallbackQuery,
#     state: FSMContext,
# ) -> None:
#     evening_movie = query.data.split(':')[1]
#     await state.update_data(evening_movie=evening_movie)
#     await state.set_state(RegistrationState.lifestyle)
#     answer_text = evening_movie_bot_answers.get(evening_movie)
#     await query.message.edit_text(
#         f'{answer_text}\n\nТвой способ пережить сложный день — это скорее',
#         reply_markup=get_lifestyles_kb(),
#     )


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

        await state.set_state(RegistrationState.territory)
        answer_text = lifestyles_bot_answers.get(frozenset(lifestyles))
        await query.message.edit_text(
            f'{answer_text}\n\nГде ты чувствуешь себя «своим»?\n\n'
            f'{territories_text}',
            reply_markup=get_territories_kb(),
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
    F.data.startswith('territory'),
    StateFilter(RegistrationState.territory),
)
async def set_territory_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    territory = query.data.split(':')[1]
    await state.update_data(territory=territory)
    await state.set_state(RegistrationState.interest)
    answer_text = territory_bot_answers[territory]
    await query.message.edit_text(
        answer_text,
        reply_markup=await get_interests_kb(territory),
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
    interest = await Interest.objects.aget(pk=callback_data.pk)
    await state.update_data(interest_id=interest.pk)
    await state.set_state(RegistrationState.career_focus)
    await query.message.edit_text(
        career_focuses_text,
        reply_markup=get_career_focuses_kb(),
    )


@router.message(F.text, StateFilter(RegistrationState.interest))
async def set_interest_message_handler(
    msg: Message,
    state: FSMContext,
) -> None:
    interest, _ = await Interest.objects.aget_or_create(name=msg.text)
    await state.update_data(interest_id=interest.pk)
    await state.set_state(RegistrationState.career_focus)
    await msg.answer(
        career_focuses_text,
        reply_markup=get_career_focuses_kb(),
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

    questions_ids = [
        i
        async for i in Question.objects.filter(
            key__in=['money_habits', 'share_skill_card'],
        )
        .order_by('order')
        .values_list('pk', flat=True)
    ]
    question = await Question.objects.prefetch_related('answers').aget(
        pk=questions_ids[0],
    )

    await state.update_data(
        career_focus_direction_id=career_focus_direction.pk,
        questions_ids=questions_ids,
        current_question_index=1,
        next_question_function_key='ask_search_type',
    )
    await state.set_state(RegistrationState.questions)
    await query.message.edit_text(
        question.text,
        reply_markup=get_answers_kb(question.answers.all()),
    )


@router.callback_query(action_filter('answer', 'select', detail=True))
async def select_answer_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: IntDetailActionCallback,
) -> None:
    data = await state.get_data()

    current_question_index = data.get('current_question_index', 0)
    current_question_index += 1
    questions_ids = data.get('questions_ids', [])
    next_question_function_key = data['next_question_function_key']

    answers_ids = data.get('answers_ids', [])
    answers_ids.append(callback_data.pk)

    if current_question_index >= len(questions_ids):
        next_question_func = _questions_handlers[next_question_function_key]
        await next_question_func(query, state)
        return

    answer = await Answer.objects.select_related('question').aget(
        pk=callback_data.pk,
    )
    question = await Question.objects.prefetch_related('answers').aget(
        pk=current_question_index,
    )

    await state.set_data(
        **data,
        **{
            'answers_ids': answers_ids,
            'current_question_index': current_question_index,
        },
    )

    bot_response = answer.bot_response or answer.question.bot_response
    text = (
        f'{bot_response}\n\n{question.text}' if bot_response else question.text
    )
    await query.message.edit_text(
        text,
        reply_markup=get_answers_kb(question.answers.all()),
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
    question_keys = ['communication_style']
    await state.update_data(
        search_type=search_type,
        questions_ids=[
            i
            async for i in Question.objects.filter(
                key__in=question_keys,
            ).values_list('pk', flat=True)
        ],
        next_question_function_key='ask_match_type',
    )
    await state.set_state(RegistrationState.questions)
    question = await Question.objects.prefetch_related('answers').aget(
        key=question_keys[0],
    )
    await query.message.edit_text(
        f'Хм, интересный запрос. Записываю приоритеты.\n\n{question.text}',
        reply_markup=get_answers_kb(question.answers.all()),
    )


@router.callback_query(
    F.data.startswith('match_type'),
    StateFilter(RegistrationState.match_type),
)
async def set_match_type_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    match_type = query.data.split(':')[1]
    await state.update_data(match_type=match_type)
    await state.set_state(RegistrationState.workday_type)
    await query.message.edit_text(
        'Координаты заданы. Иду искать совпадение.\n\n'
        'И последний штрих! Чтобы общение было максимально комфортным, '
        'расскажи, где проходит твой рабочий день?',
        reply_markup=get_workday_types_kb(),
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

    # await Profile.objects.filter(user=user).adelete()
    profile = await Profile.objects.acreate(
        user=user,
        name=data['name'],
        gender=data['gender'],
        city_id=data['city_id'],
        department_id=data['department_id'],
        interest_id=data['interest_id'],
        career_focus_direction_id=data['career_focus_direction_id'],
        search_type=data['search_type'],
        match_type=data['match_type'],
        workday_type=workday_type,
    )
    await ProfileLifestyle.objects.abulk_create(
        [
            ProfileLifestyle(profile=profile, lifestyle=lifestyle)
            for lifestyle in data['lifestyles']
        ],
    )
    await UserAnswer.objects.abulk_create(
        [
            UserAnswer(profile=profile, answer_id=answer_id)
            for answer_id in data.get('answers_ids', [])
        ],
    )

    matched_user = await find_match(user)
    if not matched_user:
        await query.message.edit_text(
            'Готово! Твой профиль в игре.\n\n'
            'Теперь моя очередь: '
            'ищу собеседника, который разделит твои идеи и зарядит энергией. '
            'Мы ценим твой подход — подбор будет максимально точным под твои цели.\n\n'
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


async def ask_search_type(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationState.search_type)
    await query.message.edit_text(
        'Хочешь найти собеседника',
        reply_markup=get_search_types_kb(),
    )


async def ask_match_type(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationState.match_type)
    await query.message.edit_text(
        'Твой идеальный мэтч — это',
        reply_markup=get_match_types_kb(),
    )


async def ask_lifestyle(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationState.lifestyle)
    await query.message.edit_text(
        f'{query.message.text}\n\nТвой способ пережить сложный день — это скорее',
        reply_markup=get_lifestyles_kb(),
    )


_questions_handlers = {
    'ask_search_type': ask_search_type,
    'ask_match_type': ask_match_type,
    'ask_lifestyle': ask_lifestyle,
}
