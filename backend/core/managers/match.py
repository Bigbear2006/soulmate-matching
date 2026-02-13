from typing import TYPE_CHECKING

from django.db.models import QuerySet

from core.choices import MatchStatus
from core.managers.base import BaseManager

if TYPE_CHECKING:
    from core.models import Match


class MatchManager(BaseManager['Match']):
    def get_queryset(self) -> QuerySet['Match']:
        return (
            super()
            .get_queryset()
            .select_related('initiator__profile', 'recipient__profile')
        )

    async def close(self, pk: int) -> None:
        await self.update_by_id(pk, status=MatchStatus.CLOSED)
