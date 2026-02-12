from typing import TYPE_CHECKING

from django.db.models import QuerySet

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
