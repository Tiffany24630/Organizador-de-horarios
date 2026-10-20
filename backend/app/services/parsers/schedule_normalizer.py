from app.services.parsers.day_mapper import normalize_day
from app.services.parsers.value_normalizer import normalize_text

def normalize_rows(dataframe, mapping):
    rows = []

    source = (row for _, row in dataframe.iterrows()) if hasattr(dataframe, "iterrows") else dataframe
    for row in source:
        normalized = {
                "activity": normalize_text(row[mapping["activity"]]),
                "day": row[mapping["day"]],
                "start": row[mapping["start"]],
                "end": row[mapping["end"]],
            }
        try:
            normalized["day"] = normalize_day(normalized["day"])
        except ValueError:
            pass
        if "room" in mapping:
            value = row.get(mapping["room"]) if hasattr(row, "get") else row[mapping["room"]]
            normalized["room"] = normalize_text(value) if value not in (None, "") else None
        rows.append(normalized)

    return rows
