import asyncio
import functools
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

from celery import Task, shared_task

Task.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)  # type: ignore[attr-defined]

_P = ParamSpec('_P')
_R = TypeVar('_R')


def async_shared_task(
    func: Callable[_P, Coroutine[Any, Any, _R]],
) -> Task[_P, _R]:
    @shared_task
    @functools.wraps(func)
    def decorator(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        loop = getattr(async_shared_task, 'loop', None)
        if not loop:
            loop = asyncio.new_event_loop()
            async_shared_task.loop = loop  # type: ignore[attr-defined]
        return loop.run_until_complete(func(*args, **kwargs))

    return decorator
