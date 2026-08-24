from app.services.parsers.column_detector import detect_columns
from app.services.parsers.schedule_normalizer import normalize_rows

def parse_dataframe(dataframe):
    columns = dataframe.columns if hasattr(dataframe, "columns") else (dataframe[0].keys() if dataframe else [])
    mapping = detect_columns(columns)

    required = ["activity", "day", "start", "end"]

    missing = []

    for field in required:
        if field not in mapping:
            missing.append(field)

    if missing:
        return {
            "success": False,
            "error": "Missing columns: " + ", ".join(missing)
        }

    rows = normalize_rows(dataframe, mapping)

    return {
        "success": True,
        "schedule": rows
    }
