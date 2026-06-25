from datetime import datetime
from collections import defaultdict

def parse_time(value):
    """
    Convierte string u objeto a datetime.time
    """
    if hasattr(value, "time"):
        return value.time()

    value = str(value).strip()
    formats = ["%H:%M", "%H:%M:%S"]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        
        except Exception:
            continue

    raise ValueError(f"Invalid time format: {value}")

def validate_time_order(start, end):
    return start < end

def detect_overlaps(blocks):
    """
    Detecta traslapes por día
    """

    errors = []
    grouped = defaultdict(list)

    for b in blocks:
        grouped[b["day"]].append(b)

    for day, items in grouped.items():
        items.sort(key=lambda x: x["start"])

        for i in range(len(items) - 1):
            current = items[i]
            next_block = items[i + 1]

            if current["end"] > next_block["start"]:
                errors.append({
                    "type": "OVERLAP",
                    "day": day,
                    "conflict": {
                        "block_1": current,
                        "block_2": next_block
                    }
                })

    return errors

def validate_schedule(schedule):
    """
    Valida estructura completa del horario importado
    """

    errors = []
    cleaned = []

    for i, row in enumerate(schedule):
        try:
            activity = row.get("activity")
            day = row.get("day")
            start = row.get("start")
            end = row.get("end")

            if not all([activity, day, start, end]):
                errors.append({
                    "type": "MISSING_FIELD",
                    "row": i,
                    "data": row
                })
                continue

            start_time = parse_time(start)
            end_time = parse_time(end)

            if not validate_time_order(start_time, end_time):
                errors.append({
                    "type": "INVALID_TIME_ORDER",
                    "row": i,
                    "data": row
                })
                continue

            cleaned.append({
                "activity": activity,
                "day": day,
                "start": start_time,
                "end": end_time
            })

        except Exception as e:
            errors.append({
                "type": "PARSE_ERROR",
                "row": i,
                "error": str(e),
                "data": row
            })

    overlap_errors = detect_overlaps(cleaned)

    return {
        "valid": len(errors) == 0 and len(overlap_errors) == 0,
        "cleaned": cleaned,
        "errors": errors + overlap_errors
    }