import unicodedata

ACTIVITY_NAMES = ["actividad", "activity", "asignatura", "curso", "course", "materia", "subject", "evento", "event", "nombre"]
DAY_NAMES = ["dia", "day", "fecha"]
START_NAMES = ["inicio", "hora inicio", "hora inicial", "hora de inicio", "start", "desde", "entrada"]
END_NAMES = ["fin", "hora fin", "hora final", "hora de finalizacion", "hora de fin", "end", "hasta", "salida"]
ROOM_NAMES = ["salon", "aula", "classroom", "room", "espacio", "sala"]


def _plain(value):
    text = str(value or "").strip().lower()
    if "ã" in text or "â" in text:
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    text = unicodedata.normalize("NFKD", text)
    return "".join(character for character in text if not unicodedata.combining(character))


def find_match(column, aliases):
    normalized = _plain(column)
    return any(alias in normalized for alias in aliases)


def detect_columns(columns):
    mapping = {}
    for column in columns:
        if find_match(column, ACTIVITY_NAMES) and "activity" not in mapping:
            mapping["activity"] = column
        elif find_match(column, DAY_NAMES) and "day" not in mapping:
            mapping["day"] = column
        elif find_match(column, START_NAMES) and "start" not in mapping:
            mapping["start"] = column
        elif find_match(column, END_NAMES) and "end" not in mapping:
            mapping["end"] = column
        elif find_match(column, ROOM_NAMES) and "room" not in mapping:
            mapping["room"] = column
    return mapping
