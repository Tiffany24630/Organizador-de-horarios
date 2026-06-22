def parse_dataframe(dataframe):
    mapping = detect_columns(dataframe.columns)

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