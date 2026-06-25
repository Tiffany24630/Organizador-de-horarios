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

HEADER_WORDS = {
    "dia",
    "día",
    "inicio",
    "fin",
    "actividad"
}

def normalize_day(text: str):
    text = text.lower().strip()

    return DAYS.get(text)

def detect_schedule_from_table(rows):
    schedule = []

    for row in rows:
        first_column = str(row[0]).strip().lower()

        if first_column in HEADER_WORDS:
            continue
        
        if len(row) < 4:
            continue

        day = normalize_day(str(row[0]))

        if not day:
            continue

        schedule.append(
            {
                "activity": str(row[3]),
                "day": day,
                "start": str(row[1]),
                "end": str(row[2])
            }
        )

    return schedule