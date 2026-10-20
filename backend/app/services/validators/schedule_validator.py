from collections import defaultdict

from app.services.parsers.value_normalizer import normalize_row, parse_time


def validate_schedule(schedule):
    """Normalize and validate rows, retaining an error location for editing."""
    errors = []
    cleaned = []
    editable = []
    source_rows = list(schedule or [])

    for index, row in enumerate(source_rows):
        row = dict(row or {})
        try:
            if not all(row.get(field) not in (None, "") for field in ("activity", "day", "start", "end")):
                raise ValueError("activity, day, start and end are required")
            normalized = normalize_row(row)
            if normalized["end"] <= normalized["start"]:
                raise ValueError("End time must be after start time")
            cleaned.append(normalized)
            editable.append(normalized)
        except Exception as error:
            errors.append({"type": "ROW_INVALID", "row": index, "message": str(error), "data": row})
            editable.append({
                "activity": row.get("activity", ""), "day": row.get("day", ""),
                "start": row.get("start", ""), "end": row.get("end", ""), "room": row.get("room") or None,
            })

    grouped = defaultdict(list)
    for index, row in enumerate(cleaned):
        grouped[row["day"]].append((index, row))
    for day, items in grouped.items():
        items.sort(key=lambda item: item[1]["start"])
        for (left_index, left), (right_index, right) in zip(items, items[1:]):
            if left["end"] > right["start"]:
                errors.append({
                    "type": "OVERLAP", "row": right_index, "day": day,
                    "message": "El bloque se superpone con otra fila del mismo día",
                    "conflict": {"block_1": left, "block_2": right},
                })

    return {"valid": not errors, "cleaned": cleaned, "editable": editable, "errors": errors}


__all__ = ["parse_time", "validate_schedule"]
