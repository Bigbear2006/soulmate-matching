from core.models import (
    Profile,
    ProfileAnswer,
    ProfileCareerFocusDirection,
    ProfileInterest,
    ProfileLifestyle,
    User,
)


async def create_profile(
    user: User,
    *,
    name: str,
    gender: str,
    city_id: int,
    department_id: int,
    search_type: str,
    workday_type: str,
    lifestyles: list[str],
    interests_ids: list[int],
    career_focus_direction_ids: list[int],
    answers_ids: list[int],
) -> Profile:
    profile, _ = await Profile.objects.aupdate_or_create(
        {
            'name': name,
            'gender': gender,
            'city_id': city_id,
            'department_id': department_id,
            'search_type': search_type,
            'workday_type': workday_type,
        },
        user=user,
    )
    await ProfileLifestyle.objects.abulk_create(
        [
            ProfileLifestyle(profile=profile, lifestyle=lifestyle)
            for lifestyle in lifestyles
        ],
        ignore_conflicts=True,
    )
    await ProfileInterest.objects.abulk_create(
        [
            ProfileInterest(profile=profile, interest_id=interest)
            for interest in interests_ids
        ],
        ignore_conflicts=True,
    )
    await ProfileCareerFocusDirection.objects.abulk_create(
        [
            ProfileCareerFocusDirection(
                profile=profile,
                career_focus_direction_id=direction,
            )
            for direction in career_focus_direction_ids
        ],
        ignore_conflicts=True,
    )
    await ProfileAnswer.objects.abulk_create(
        [
            ProfileAnswer(profile=profile, answer_id=answer_id)
            for answer_id in answers_ids
        ],
        ignore_conflicts=True,
    )
    return profile
