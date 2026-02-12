from types import TracebackType
from typing import Any, Self

from aiohttp import ClientSession
from yarl import URL


class APIClient:
    def __init__(
        self,
        base_url: str | URL | None = None,
        **session_kwargs: Any,
    ) -> None:
        self.session = ClientSession(base_url, **session_kwargs)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.session.close()
