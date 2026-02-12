import asyncio
from asyncio import Future
from collections.abc import Iterable
from typing import TypeVar

_FT = TypeVar('_FT')


async def asyncio_wait(
    fs: Iterable[Future[_FT]],
    *,
    timeout: int | float | None = None,
    return_when: str = asyncio.ALL_COMPLETED,
) -> tuple[set[Future[_FT]], set[Future[_FT]]]:
    if not fs:
        return set(), set()
    return await asyncio.wait(fs, timeout=timeout, return_when=return_when)
