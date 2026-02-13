from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.callback_data import IntDetailActionCallback
from bot.filters import action_filter
from bot.keyboards.registration import (
    get_answers_kb,
    get_lifestyles_kb,
    get_search_types_kb,
    get_workday_types_kb,
    get_yes_no_kb,
)
from bot.states import RegistrationState
from core.models import Answer, Question

router = Router()


@router.callback_query(action_filter('answer', 'select', detail=True))
async def select_answer_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: IntDetailActionCallback,
) -> None:
    data = await state.get_data()
    current_question_index = data.get('current_question_index', 0)
    questions_ids = data.get('questions_ids', [])

    answers_ids = data.get('answers_ids', [])
    if callback_data.pk in answers_ids:
        answers_ids.remove(callback_data.pk)
    else:
        answers_ids.append(callback_data.pk)

    data['answers_ids'] = answers_ids
    await state.set_data(data)

    question = await Question.objects.prefetch_related('answers').aget(
        pk=questions_ids[current_question_index],
    )
    answers = '\n'.join(
        [
            a.text
            async for a in Answer.objects.filter(
                pk__in=answers_ids,
                question=question,
            )
        ],
    )

    await query.message.edit_text(
        f'{question.text}\n\nТы выбрал:\n{answers}',
        reply_markup=get_answers_kb(question.answers.all()),
    )


@router.callback_query(F.data == 'answer:done')
async def answer_done_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    current_question_index = data.get('current_question_index', 0) + 1
    questions_ids = data.get('questions_ids', [])
    next_question_function_key = data['next_question_function_key']

    data['current_question_index'] = current_question_index
    await state.set_data(data)

    if current_question_index >= len(questions_ids):
        next_question_func = _questions_handlers[next_question_function_key]
        await next_question_func(query, state)
        return

    question = await Question.objects.prefetch_related('answers').aget(
        pk=questions_ids[current_question_index],
    )
    await query.message.edit_text(
        question.text,
        reply_markup=get_answers_kb(question.answers.all()),
    )


@router.callback_query(F.data.in_(('answer:yes', 'answer:no')))
async def answer_yes_no_handler(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    yes = query.data.split(':')[1] == 'yes'

    data = await state.get_data()
    current_answer_id = data['current_answer_id']
    answers_ids = data.get('answers_ids', [])

    if yes and current_answer_id not in answers_ids:
        answers_ids.append(current_answer_id)

    current_yes_no_answers_ids = data.get('current_yes_no_answers_ids', [])
    if not current_yes_no_answers_ids:
        await answer_done_handler(query, state)
        return

    current_answer = await Answer.objects.select_related('question').aget(
        pk=current_yes_no_answers_ids.pop(0),
    )
    data['current_answer_id'] = current_answer.pk
    data['current_yes_no_answers_ids'] = current_yes_no_answers_ids
    data['answers_ids'] = answers_ids
    await state.set_data(data)
    await query.message.edit_text(
        f'{current_answer.question.text}\n\n{current_answer.text}',
        reply_markup=get_yes_no_kb(),
    )


async def ask_search_type(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationState.search_type)
    await query.message.edit_text(
        'Хочешь найти собеседника',
        reply_markup=get_search_types_kb(),
    )


async def ask_workday_type(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationState.workday_type)
    await query.message.edit_text(
        'Координаты заданы. Иду искать совпадение.\n\n'
        'И последний штрих! Чтобы общение было максимально комфортным, '
        'расскажи, где проходит твой рабочий день?',
        reply_markup=get_workday_types_kb(),
    )


async def ask_lifestyle(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationState.lifestyle)
    await query.message.edit_text(
        'Твой способ пережить сложный день — это скорее',
        reply_markup=get_lifestyles_kb(),
    )


_questions_handlers = {
    'ask_search_type': ask_search_type,
    'ask_workday_type': ask_workday_type,
    'ask_lifestyle': ask_lifestyle,
}
