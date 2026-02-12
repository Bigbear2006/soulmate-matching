from dataclasses import dataclass

from django.db.models import Count, F, Q

from core.choices import MatchStatus
from core.models import Match, User

MAX_MATCHES_COUNT = 3


@dataclass
class Soulmate:
    user: User
    match: Match
    thread_id: int


async def find_match(user: User) -> User | None:
    matched_user = (
        await User.objects.annotate(
            initiated_matches_count=Count(
                'initiated_matches',
                filter=Q(initiated_matches__status=MatchStatus.ACTIVE),
            ),
            received_matches_count=Count(
                'received_matches',
                filter=Q(initiated_matches__status=MatchStatus.ACTIVE),
            ),
            total_matches_count=F('initiated_matches_count')
            + F('received_matches_count'),
            # answers_count=Count('user__profile__answers'),
            # matched_answers_count=Count(
            #     'user__profile__answers',
            #     filter=Q(
            #         profile__answers__answer_id__in=UserAnswer.objects.filter(
            #             profile__user=user,
            #         ).values_list('answer_id', flat=True),
            #     ),
            # ),
            # matched_answers_percentage=F('matched_answers_count')
            # / F('answers_count'),
        )
        .filter(
            ~Q(pk=user.pk),
            total_matches_count__lte=MAX_MATCHES_COUNT,
            profile__isnull=False,
            # matched_answers_percentage__gte=80,
        )
        .order_by('total_matches_count')
        .afirst()
    )
    return matched_user


async def get_soulmate(thread_id: int) -> Soulmate:
    match = await Match.objects.get_or_none(initiator_thread_id=thread_id)
    if match:
        return Soulmate(
            user=match.recipient,
            match=match,
            thread_id=match.recipient_thread_id,
        )

    match = await Match.objects.aget(recipient_thread_id=thread_id)
    return Soulmate(
        user=match.initiator,
        match=match,
        thread_id=match.initiator_thread_id,
    )
