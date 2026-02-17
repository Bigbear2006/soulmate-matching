from dataclasses import dataclass
from typing import Any

from django.db.models import Count, Exists, ExpressionWrapper, F, OuterRef, Q
from django.db.models.fields import FloatField

from bot.loader import bot
from core.choices import MatchStatus, SearchType
from core.models import (
    Match,
    ProfileAnswer,
    ProfileCareerFocusDirection,
    ProfileInterest,
    ProfileLifestyle,
    User,
)

MAX_MATCHES_COUNT = 1

MIN_MATCHED_ANSWERS_PERCENTAGE = 0.8
MIN_MATCHED_INTERESTS_COUNT = 2
MIN_MATCHED_LIFESTYLES_COUNT = 1
MIN_MATCHED_DIRECTIONS_COUNT = 1


@dataclass
class Soulmate:
    user: User
    match: Match
    thread_id: int

    def __str__(self) -> str:
        return self.user.profile.name


async def find_matched_user(user: User) -> User | None:
    profile = user.profile
    user_answers = ProfileAnswer.objects.filter(profile=profile).values_list(
        'answer_id',
        flat=True,
    )
    user_interests = ProfileInterest.objects.filter(
        profile=profile,
    ).values_list('interest_id', flat=True)
    user_lifestyles = ProfileLifestyle.objects.filter(
        profile=profile,
    ).values_list('lifestyle', flat=True)
    user_directions = ProfileCareerFocusDirection.objects.filter(
        profile=profile,
    ).values_list('career_focus_direction_id', flat=True)

    base_filter = Q(~Q(pk=user.pk)) & Q(profile__isnull=False)
    if profile.search_type == SearchType.CITY:
        base_filter &= Q(profile__city=profile.city_id)
    elif profile.search_type == SearchType.DEPARTMENT:
        base_filter &= Q(profile__department=profile.department_id)
    elif profile.search_type == SearchType.GENDER:
        base_filter &= Q(profile__gender=profile.gender)

    matched_user = (
        await User.objects.filter(base_filter)
        .annotate(
            match_exists=Exists(
                Match.objects.filter(
                    Q(initiator=OuterRef('pk'), recipient=user.pk)
                    | Q(initiator=user.pk, recipient=OuterRef('pk')),
                ),
            ),
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
            answers_count=Count('profile__answers', distinct=True),
        )
        .filter(
            match_exists=False,
            total_matches_count__lte=MAX_MATCHES_COUNT,
            answers_count__gt=0,
        )
        .annotate(
            matched_answers_count=Count(
                'profile__answers',
                filter=Q(profile__answers__answer_id__in=user_answers),
                distinct=True,
            ),
            matched_answers_percentage=ExpressionWrapper(
                F('matched_answers_count') / F('answers_count'),
                output_field=FloatField(),
            ),
            matched_interests_count=Count(
                'profile__interests',
                filter=Q(profile__interests__interest_id__in=user_interests),
                distinct=True,
            ),
            matched_lifestyles_count=Count(
                'profile__lifestyles',
                filter=Q(profile__lifestyles__lifestyle__in=user_lifestyles),
                distinct=True,
            ),
            matched_directions_count=Count(
                'profile__career_focus_directions',
                filter=Q(
                    profile__career_focus_directions__career_focus_direction_id__in=user_directions,
                ),
                distinct=True,
            ),
        )
        .filter(
            matched_answers_percentage__gte=MIN_MATCHED_ANSWERS_PERCENTAGE,
            matched_interests_count__gte=MIN_MATCHED_INTERESTS_COUNT,
            matched_lifestyles_count__gte=MIN_MATCHED_LIFESTYLES_COUNT,
            matched_directions_count__gte=MIN_MATCHED_DIRECTIONS_COUNT,
        )
        .order_by(
            '-matched_answers_percentage',
            '-matched_interests_count',
            '-matched_lifestyles_count',
            '-matched_directions_count',
            'total_matches_count',
        )
        .afirst()
    )
    return matched_user


async def find_all_matches() -> dict[int, dict[str, Any]]:
    matches_info = {}
    matches_info_fields = (
        'matched_answers_percentage',
        'matched_interests_count',
        'matched_lifestyles_count',
        'matched_directions_count',
    )

    async for user in User.objects.all():
        matched_user = await find_matched_user(user)
        if not matched_user:
            continue
        matches_info[user.pk] = {
            field_name: value
            for field_name in matches_info_fields
            if (value := getattr(user, field_name, None))
        }
        matches_info[user.pk]['matched_user_id'] = matched_user.pk
        # do not create matches for now
        # await create_match(user, matched_user)

    return matches_info


async def create_match(user: User, matched_user: User) -> Match:
    initiator_topic = await bot.create_forum_topic(
        user.pk,
        name=matched_user.profile.name,
    )
    recipient_topic = await bot.create_forum_topic(
        matched_user.id,
        name=user.profile.name,
    )
    return await Match.objects.acreate(
        initiator=user,
        initiator_thread_id=initiator_topic.message_thread_id,
        recipient=matched_user,
        recipient_thread_id=recipient_topic.message_thread_id,
    )


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
