from django.db.models.enums import TextChoices


class Gender(TextChoices):
    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'


class EveningMovie(TextChoices):
    IRONY = 'irony', 'Ирония судьбы, или С лёгким паром!'
    OPERATION_Y = 'operation_y', 'Операция Ы и другие приключения Шурика'
    MOSCOW = 'moscow', 'Москва слезам не верит'
    DOG_HEART = 'dog_heart', 'Собачье сердце'
    IVAN = 'ivan', 'Иван Васильевич меняет профессию'


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


class MatchStatus(TextChoices):
    ACTIVE = 'active', 'Активен'
    CLOSED = 'closed', 'Завершен'


class ExchangeStatus(TextChoices):
    PENDING = 'pending', 'Ожидает ответа'
    ACCEPTED = 'accepted', 'Принят'
    DECLINED = 'declined', 'Отклонен'
