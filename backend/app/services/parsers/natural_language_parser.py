import re

def parse_time_range(text):
    pattern = r"(\d{1,2}:\d{2})"
    matches = re.findall(pattern, text)

    if len(matches) >= 2:
        return {
            "start": matches[0],
            "end": matches[1]
        }

    return None

def parse_forbidden_day(text):
    text = text.lower()

    days = [
        "lunes",
        "martes",
        "miercoles",
        "miércoles",
        "jueves",
        "viernes",
        "sabado",
        "sábado",
        "domingo"
    ]

    for day in days:
        if day in text:
            return day

    return None