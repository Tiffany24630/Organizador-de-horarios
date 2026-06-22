COLUMN_ALIASES = {
    "activity": [
        "actividad",
        "curso",
        "materia",
        "clase",
        "evento",
        "actividad nombre",
        "subject",
        "activity"
    ],

    "day": [
        "dia",
        "día",
        "day"
    ],

    "start": [
        "inicio",
        "hora inicio",
        "entrada",
        "start",
        "start time"
    ],

    "end": [
        "fin",
        "hora fin",
        "salida",
        "end",
        "end time"
    ]
}

def detect_columns(df):
    result = {}

    columns = [str(col).strip().lower()
        for col in df.columns
    ]

    for field, aliases in COLUMN_ALIASES.items():
        result[field] = None

        for column in columns:
            if column in aliases:
                result[field] = column
                break

    return result