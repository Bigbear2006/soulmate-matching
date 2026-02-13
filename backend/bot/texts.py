from core.choices import Lifestyle, Territory

lifestyles_bot_answers = {
    frozenset([Lifestyle.TALK]): (
        'Тогда тебе нужен человек с функцией «внимательное ухо». Учту.'
    ),
    frozenset([Lifestyle.DISTRACT]): (
        'Значит, ты – тот самый эмпатичный слушатель. '
        'Буду искать тебе собеседника, которому точно есть что рассказать.'
    ),
    frozenset([Lifestyle.PHYSICAL]): (
        'Отлично. Значит, возможны мэтчи «пойдем пробежимся» '
        'вместо «пойдем обсудим».'
    ),
    frozenset([Lifestyle.TALK, Lifestyle.PHYSICAL]): (
        'И поговорить, и подвигаться. Баланс – это красиво.'
    ),
    frozenset([Lifestyle.TALK, Lifestyle.DISTRACT]): (
        'Мастер коммуникации! Можешь и выговориться, и выслушать — '
        'идеальный сценарий для глубокого общения.'
    ),
    frozenset([Lifestyle.DISTRACT, Lifestyle.PHYSICAL]): (
        'Переключиться через движение и чужие истории — отличная стратегия.'
    ),
    frozenset(
        [
            Lifestyle.TALK,
            Lifestyle.DISTRACT,
            Lifestyle.PHYSICAL,
        ],
    ): (
        'Ты универсальный человек! И выслушаешь, и выскажешься, '
        'и на пробежку сходишь!'
    ),
}

territory_descriptions: dict[str, str] = {
    Territory.ENERGY: '«Тренировка тела открывает путь тренировке ума»',
    Territory.LAMPOVO: '«Люблю провести время со вкусом»',
    Territory.HEDONISM: (
        '«Жизнь слишком коротка для невкусной еды и скучных выходных»'
    ),
    Territory.MEANING: '«Играть, учиться, обсуждать»',
    Territory.FAMILY: '«Про жизнь, семью и быт»',
}
