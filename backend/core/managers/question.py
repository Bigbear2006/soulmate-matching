from typing import TYPE_CHECKING

from core.choices import QuestionKey
from core.managers.base import BaseManager

if TYPE_CHECKING:
    from core.models import Question  # noqa


class QuestionManager(BaseManager['Question']):
    async def get_ids_for_keys(
        self,
        keys: list[str | QuestionKey],
    ) -> list[int]:
        return [
            i
            async for i in self.filter(key__in=keys)
            .order_by('order')
            .values_list(
                'pk',
                flat=True,
            )
        ]
