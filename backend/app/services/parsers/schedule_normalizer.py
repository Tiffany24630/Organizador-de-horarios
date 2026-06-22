from app.models.enums import DayOfWeek

DAY_MAPPING = {
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

def normalize_day(day):
    if day is None:
        return None

    day = str(day).lower().strip()

    return DAY_MAPPING.get(day)


def normalize_schedule(df, mapping):
    records = []

    for _, row in df.iterrows():
        records.append(
            {
                "activity": row[mapping["activity"]],
                "day": normalize_day(row[mapping["day"]]),
                "start": str(row[mapping["start"]]),
                "end": str(row[mapping["end"]])
            }
        )

    return records