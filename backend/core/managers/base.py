from typing import Any, Generic, TypeVar

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

_Model = TypeVar('_Model', bound=models.Model)


class BaseManager(Generic[_Model], models.Manager[_Model]):
    async def get_or_none(self, **kwargs: Any) -> _Model | None:
        try:
            return await self.aget(**kwargs)
        except ObjectDoesNotExist:
            return None

    async def update_by_id(self, pk: int, **kwargs: Any) -> int:
        return await self.filter(pk=pk).aupdate(**kwargs)

    async def delete_by_id(self, pk: int) -> tuple[int, dict[str, int]]:
        return await self.filter(pk=pk).adelete()
