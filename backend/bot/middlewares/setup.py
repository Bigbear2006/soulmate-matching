from aiogram import BaseMiddleware, Router


def setup_middlewares(
    router: Router,
    *middlewares: BaseMiddleware,
    include_events: set[str] | None = None,
    exclude_events: set[str] | None = None,
) -> None:
    if not include_events:
        include_events = {'message', 'callback_query'}
    if not exclude_events:
        exclude_events = set()
    exclude_events = {'update', *exclude_events}
    for event, observer in router.observers.items():
        if event in exclude_events or event not in include_events:
            continue
        for middleware in middlewares:
            observer.middleware(middleware)
