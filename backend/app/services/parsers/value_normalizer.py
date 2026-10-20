from datetime import datetime, time
import math
import re

from app.services.parsers.day_mapper import normalize_day


def normalize_text(value):
    return " ".join(str(value or "").replace("\n", " ").split())


def parse_time(value):
    """Parse Excel/Python/string time values into datetime.time."""
    if isinstance(value, datetime):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Invalid numeric time: {value}")
        fraction = value % 1
        total_minutes = round(fraction * 24 * 60)
        if total_minutes >= 24 * 60:
            total_minutes = 0
        return time(total_minutes // 60, total_minutes % 60)

    text = normalize_text(value).upper().replace("．", ":")
    text = re.sub(r"\s*([AP])\.?\s*M\.?$", r" \1M", text)
    text = text.replace(".", ":") if re.fullmatch(r"\d{1,2}\.\d{2}(?:\s*[AP]M)?", text) else text
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p", "%I:%M:%S %p"):
        try:
            return datetime.strptime(text, fmt).time().replace(second=0, microsecond=0)
        except ValueError:
            continue
    raise ValueError(f"Invalid time: {value}")


def normalize_row(row):
    normalized = {
        "activity": normalize_text(row.get("activity")),
        "day": normalize_day(row.get("day")),
        "start": parse_time(row.get("start")),
        "end": parse_time(row.get("end")),
    }
    room = normalize_text(row.get("room"))
    if room:
        normalized["room"] = room
    return normalized
