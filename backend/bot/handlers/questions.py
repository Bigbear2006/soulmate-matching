from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.callback_data import IntDetailActionCallback
from bot.filters import action_filter
from bot.keyboards.registration import (
    get_answers_kb,
    get_lifestyles_kb,
    get_match_types_kb,
    get_search_types_kb,
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
    current_question_index += 1
    questions_ids = data.get('questions_ids', [])
    next_question_function_key = data['next_question_function_key']

    answers_ids = data.get('answers_ids', [])
    answers_ids.append(callback_data.pk)

    data['answers_ids'] = answers_ids
    data['current_question_index'] = current_question_index
    await state.set_data(data)

    answer = await Answer.objects.select_related('question').aget(
        pk=callback_data.pk,
    )
    bot_response = answer.bot_response or answer.question.bot_response

    if current_question_index >= len(questions_ids):
        next_question_func = _questions_handlers[next_question_function_key]
        await next_question_func(query, state)
        return

    question = await Question.objects.prefetch_related('answers').aget(
        pk=questions_ids[current_question_index],
    )
    text = (
        f'{bot_response}\n\n{question.text}' if bot_response else question.text
    )
    await query.message.edit_text(
        text,
        reply_markup=get_answers_kb(question.answers.all()),
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
        'Твой способ пережить сложный день — это скорее',
        reply_markup=get_lifestyles_kb(),
    )


_questions_handlers = {
    'ask_search_type': ask_search_type,
    'ask_match_type': ask_match_type,
    'ask_lifestyle': ask_lifestyle,
}
