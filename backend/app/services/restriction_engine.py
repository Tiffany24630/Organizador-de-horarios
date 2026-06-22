from sqlalchemy.orm import Session
from app.models.activity_group import ActivityGroup
from app.models.enums import RestrictionType

def apply_restrictions(matrix: dict, group: ActivityGroup):
    restrictions = group.restrictions

    for restriction in restrictions:
        if (restriction.type == RestrictionType.FORBIDDEN_DAY):
            day = restriction.day_of_week.value

            if day in matrix:
                for slot in matrix[day]:
                    matrix[day][slot] = 0

        elif (restriction.type == RestrictionType.ALLOWED_HOURS):
            for day in matrix:
                for slot in matrix[day]:
                    if (
                        slot < restriction.start_time.strftime("%H:%M")
                        or
                        slot >= restriction.end_time.strftime("%H:%M")
                    ):
                        matrix[day][slot] = 0

        elif (restriction.type == RestrictionType.FORBIDDEN_HOURS):
            for day in matrix:
                for slot in matrix[day]:
                    if (restriction.start_time.strftime("%H:%M") <= slot < restriction.end_time.strftime("%H:%M")):
                        matrix[day][slot] = 0

    return matrix