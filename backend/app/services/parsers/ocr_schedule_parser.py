import re
from app.services.parsers.day_mapper import normalize_day


def parse_schedule_text(text: str):
    schedule = []

    lines = text.splitlines()

    pattern = re.compile(r"([A-Za-záéíóúÁÉÍÓÚñÑ]+)\s+(\d{1,2}:\d{2})[-\s]+(\d{1,2}:\d{2})\s+(.+)")

    for line in lines:
        line = line.strip()

        if not line:
            continue

        match = pattern.match(line)

        if not match:
            continue

        day, start, end, activity = match.groups()

        try:
            schedule.append(
                {
                    "activity": activity.strip(),
                    "day": normalize_day(day),
                    "start": start,
                    "end": end
                }
            )

        except Exception:
            continue

    return schedule