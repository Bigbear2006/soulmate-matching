from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    name = State()
    gender = State()
    city = State()
    department = State()
    lifestyle = State()
    interest = State()
    career_focus = State()
    career_focus_direction = State()
    search_type = State()
    match_type = State()
    workday_type = State()
    questions = State()
