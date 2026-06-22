from app.models.enums import DayOfWeek

DAY_MAP = {
    "lunes": DayOfWeek.MONDAY,
    "monday": DayOfWeek.MONDAY,

    "martes": DayOfWeek.TUESDAY,
    "tuesday": DayOfWeek.TUESDAY,

    "miercoles": DayOfWeek.WEDNESDAY,
    "miércoles": DayOfWeek.WEDNESDAY,
    "wednesday": DayOfWeek.WEDNESDAY,

    "jueves": DayOfWeek.THURSDAY,
    "thursday": DayOfWeek.THURSDAY,

    "viernes": DayOfWeek.FRIDAY,
    "friday": DayOfWeek.FRIDAY,

    "sabado": DayOfWeek.SATURDAY,
    "sábado": DayOfWeek.SATURDAY,
    "saturday": DayOfWeek.SATURDAY,

    "domingo": DayOfWeek.SUNDAY,
    "sunday": DayOfWeek.SUNDAY
}

def normalize_day(value):
    value = str(value).strip().lower()

    if value not in DAY_MAP:
        raise ValueError(f"Unknown day: {value}")

    return DAY_MAP[value]