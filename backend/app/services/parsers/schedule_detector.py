from app.models.enums import DayOfWeek

DAYS = {
    "lunes": DayOfWeek.MONDAY,
    "martes": DayOfWeek.TUESDAY,
    "miercoles": DayOfWeek.WEDNESDAY,
    "miércoles": DayOfWeek.WEDNESDAY,
    "jueves": DayOfWeek.THURSDAY,
    "viernes": DayOfWeek.FRIDAY,
    "sabado": DayOfWeek.SATURDAY,
    "sábado": DayOfWeek.SATURDAY,
    "domingo": DayOfWeek.SUNDAY
}

def normalize_day(text: str):
    text = text.lower().strip()

    return DAYS.get(text)

def detect_schedule_from_table(rows):
    schedule = []

    for row in rows:
        if len(row) < 4:
            continue

        day = normalize_day(str(row[0]))

        if not day:
            continue

        schedule.append(
            {
                "day": day,
                "start": str(row[1]),
                "end": str(row[2]),
                "name": str(row[3])
            }
        )

    return schedule