from django.db.models.enums import TextChoices


class Gender(TextChoices):
    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'


class Lifestyle(TextChoices):
    TALK = 'talk', 'Мне важно выговориться'
    DISTRACT = (
        'distract',
        'Мне важно отвлечься от своих мыслей, разделив переживания другого',
    )
    PHYSICAL = 'physical', 'Мне важно физически переключиться'


class Territory(TextChoices):
    ENERGY = 'energy', 'Территория Энергии'
    LAMPOVO = 'lampovo', 'Территория Ламповости'
    HEDONISM = 'hedonism', 'Территория Гедонизма'
    MEANING = 'meaning', 'Территория Смысла'
    FAMILY = 'family', 'Родственная территория'


class CareerFocus(TextChoices):
    RESULT = 'result', 'Результат'
    DEVELOPMENT = 'development', 'Развитие'
    ENJOYMENT = 'enjoyment', 'Удовольствие'


class SearchType(TextChoices):
    CITY = 'city', 'В моем городе'
    DEPARTMENT = 'department', 'В моем департаменте'
    GENDER = 'gender', 'Среди своего пола'
    INTERESTS = 'interests', 'По схожим интересам'


class MatchType(TextChoices):
    MY_CITY = 'my_city', 'Мой город'
    OTHER_CITY = 'other_city', 'Другой регион'


class WorkdayType(TextChoices):
    OFFICE = 'office', 'В офисе (люблю деловой ритм и личные встречи)'
    DEPARTMENT = 'branch', 'В отделении (я там, где наши клиенты)'
    REMOTE = 'remote', 'На удаленке (люблю работать из дома)'


class QuestionKey(TextChoices):
    EVENING_MOVIE = 'evening_movie', 'Если бы твой вечер был фильмом'
    MONEY_HABITS = 'money_habits', 'Про тебя сейчас скорее так'
    SHARE_SKILL_CARD = 'share_skill_card', 'Карта, которой ты готов поделиться'
    COMMUNICATION_STYLE = 'communication_style', 'Стиль общения'
    COMPANY_ROLE = 'company_role', 'Роль в компании'
    WHY_FUN_TO_BE_WITH = 'why_fun_to_be_with', 'Со мной классно, потому что'
    WHY_HERE = 'why_here', 'Здесь ради'


class MatchStatus(TextChoices):
    ACTIVE = 'active', 'Активен'
    CLOSED = 'closed', 'Завершен'


class ExchangeStatus(TextChoices):
    PENDING = 'pending', 'Ожидает ответа'
    ACCEPTED = 'accepted', 'Принят'
    DECLINED = 'declined', 'Отклонен'
