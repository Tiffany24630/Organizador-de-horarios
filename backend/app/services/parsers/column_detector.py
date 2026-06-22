ACTIVITY_NAMES = [
    "actividad",
    "activity",
    "curso",
    "course",
    "materia",
    "subject",
    "evento",
    "event",
    "nombre"
]

DAY_NAMES = [
    "dia",
    "día",
    "day"
]

START_NAMES = [
    "inicio",
    "hora inicio",
    "start",
    "desde",
    "entrada"
]

END_NAMES = [
    "fin",
    "hora fin",
    "end",
    "hasta",
    "salida"
]


def find_match(column, aliases):
    column = column.lower().strip()

    for alias in aliases:
        if alias in column:
            return True

    return False


def detect_columns(columns):
    mapping = {}

    for column in columns:
        if find_match(column, ACTIVITY_NAMES):
            mapping["activity"] = column

        elif find_match(column, DAY_NAMES):
            mapping["day"] = column

        elif find_match(column, START_NAMES):
            mapping["start"] = column

        elif find_match(column, END_NAMES):
            mapping["end"] = column

    return mapping