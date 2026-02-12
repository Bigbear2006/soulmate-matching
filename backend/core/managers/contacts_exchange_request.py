from typing import TYPE_CHECKING

from core.choices import ExchangeStatus
from core.managers.base import BaseManager

if TYPE_CHECKING:
    from core.models import ContactsExchangeRequest  # noqa


class ContactsExchangeRequestManager(BaseManager['ContactsExchangeRequest']):
    async def accept(self, pk: int) -> None:
        await self.update_by_id(pk=pk, status=ExchangeStatus.ACCEPTED)

    async def decline(self, pk: int) -> None:
        await self.update_by_id(pk=pk, status=ExchangeStatus.DECLINED)
