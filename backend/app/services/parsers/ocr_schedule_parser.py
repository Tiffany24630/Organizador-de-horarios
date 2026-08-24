import re

from app.services.parsers.day_mapper import normalize_day


def parse_schedule_text(text: str):
    """Parse lines such as: `Lunes 08:00-09:20 Matemática`."""
    schedule = []
    pattern = re.compile(r"([A-Za-zÁÉÍÓÚáéíóúÑñ]+)\s+(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})\s+(.+)")
    for raw_line in (text or "").splitlines():
        match = pattern.search(raw_line.strip())
        if not match:
            continue
        day, start, end, activity = match.groups()
        try:
            schedule.append({"activity": activity.strip(), "day": normalize_day(day), "start": start, "end": end})
        except ValueError:
            continue
    return schedule
