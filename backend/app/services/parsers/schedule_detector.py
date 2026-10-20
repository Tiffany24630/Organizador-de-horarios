from app.models.enums import DayOfWeek
from app.services.parsers.day_mapper import normalize_day


HEADER_WORDS = {"dia", "día", "day", "inicio", "fin", "actividad", "asignatura", "aula", "salon", "salón"}


def detect_schedule_from_table(rows):
    """Parse simple PDF tables with day/start/end/activity positional columns."""
    schedule = []
    for row in rows or []:
        if not row or len(row) < 4:
            continue
        first = str(row[0] or "").strip().lower()
        if first in HEADER_WORDS:
            continue
        try:
            day = normalize_day(row[0])
        except ValueError:
            continue
        item = {"activity": str(row[3] or "").strip(), "day": day, "start": row[1], "end": row[2]}
        if len(row) > 4 and row[4] not in (None, ""):
            item["room"] = str(row[4]).strip()
        if item["activity"]:
            schedule.append(item)
    return schedule
