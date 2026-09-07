import unicodedata

from app.models.enums import DayOfWeek


DAY_MAP = {
    "lunes": DayOfWeek.MONDAY,
    "lun": DayOfWeek.MONDAY,
    "monday": DayOfWeek.MONDAY,
    "martes": DayOfWeek.TUESDAY,
    "mar": DayOfWeek.TUESDAY,
    "tuesday": DayOfWeek.TUESDAY,
    "miercoles": DayOfWeek.WEDNESDAY,
    "mie": DayOfWeek.WEDNESDAY,
    "wednesday": DayOfWeek.WEDNESDAY,
    "jueves": DayOfWeek.THURSDAY,
    "jue": DayOfWeek.THURSDAY,
    "thursday": DayOfWeek.THURSDAY,
    "viernes": DayOfWeek.FRIDAY,
    "vie": DayOfWeek.FRIDAY,
    "friday": DayOfWeek.FRIDAY,
    "sabado": DayOfWeek.SATURDAY,
    "sab": DayOfWeek.SATURDAY,
    "saturday": DayOfWeek.SATURDAY,
    "domingo": DayOfWeek.SUNDAY,
    "dom": DayOfWeek.SUNDAY,
    "sunday": DayOfWeek.SUNDAY,
}


def normalize_day(value):
    if isinstance(value, DayOfWeek):
        return value
    normalized = unicodedata.normalize("NFKD", str(value).strip().lower())
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    if normalized not in DAY_MAP:
        raise ValueError(f"Unknown day: {value}")
    return DAY_MAP[normalized]
