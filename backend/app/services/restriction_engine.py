from app.models.activity_group import ActivityGroup
from app.models.enums import RestrictionType


def _time_minutes(value):
    return value.hour * 60 + value.minute


def restriction_reason(group: ActivityGroup, day: str, start: int, end: int):
    applicable = [item for item in group.restrictions if item.day_of_week is None or item.day_of_week.value == day]
    for restriction in applicable:
        if restriction.type == RestrictionType.FORBIDDEN_DAY:
            return f"Día prohibido por la restricción '{restriction.name}'"
        if restriction.start_time is None or restriction.end_time is None:
            continue
        restricted_start = _time_minutes(restriction.start_time)
        restricted_end = _time_minutes(restriction.end_time)
        overlap = max(0, min(end, restricted_end) - max(start, restricted_start))
        if restriction.type == RestrictionType.FORBIDDEN_HOURS and overlap:
            return f"Solapa el intervalo prohibido '{restriction.name}'"

    all_allowed = [item for item in group.restrictions if item.type == RestrictionType.ALLOWED_HOURS]
    allowed = [item for item in applicable if item.type == RestrictionType.ALLOWED_HOURS]
    if all_allowed and not allowed:
        return "No existe un intervalo permitido para este día"
    if allowed and not any(
        item.start_time is not None and item.end_time is not None
        and start >= _time_minutes(item.start_time) and end <= _time_minutes(item.end_time)
        for item in allowed
    ):
        return "Fuera de los intervalos horarios permitidos"
    return None


def apply_restrictions(matrix: dict, group: ActivityGroup):
    # Kept for compatibility with the legacy matrix engine. The precise
    # proposal generator uses restriction_reason instead of coarse slots.
    for day in matrix:
        for slot in matrix[day]:
            hour, minute = map(int, slot.split(":"))
            if restriction_reason(group, day, hour * 60 + minute, hour * 60 + minute + 1):
                matrix[day][slot] = 0
    return matrix
