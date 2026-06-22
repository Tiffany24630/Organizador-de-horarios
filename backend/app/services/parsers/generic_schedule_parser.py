from app.services.parsers.column_detector import detect_columns
from app.services.parsers.schedule_normalizer import normalize_schedule

def parse_dataframe(df):
    mapping = detect_columns(df)

    missing = []

    for field in [
        "activity",
        "day",
        "start",
        "end"
    ]:

        if mapping[field] is None:
            missing.append(field)

    if missing:
        return {
            "success": False,
            "missing": missing,
            "mapping": mapping
        }

    schedule = normalize_schedule(df, mapping)

    return {
        "success": True,
        "mapping": mapping,
        "schedule": schedule
    }