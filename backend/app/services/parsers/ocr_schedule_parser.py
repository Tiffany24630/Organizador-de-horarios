"""Parsers for schedules obtained through OCR."""

import re
from collections import defaultdict

from app.services.parsers.day_mapper import normalize_day

TIME_RANGE = re.compile(r"(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})")
DAY_LINE = re.compile(r"([A-Za-zÁÉÍÓÚáéíóúÑñ]+)\s+(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})\s+(.+)", re.IGNORECASE)


def _clean(value):
    return " ".join(str(value or "").replace("\n", " ").split())


def _is_day(value):
    try:
        return normalize_day(value)
    except ValueError:
        return None


def parse_schedule_text(text: str):
    """Parse OCR text where each entry includes its day and time range."""
    schedule = []
    for raw_line in (text or "").splitlines():
        match = DAY_LINE.search(_clean(raw_line))
        if not match:
            continue
        day, start, end, activity = match.groups()
        normalized_day = _is_day(day)
        if normalized_day and activity.strip():
            schedule.append({"activity": activity.strip(), "day": normalized_day, "start": start, "end": end})
    return schedule


def _ocr_lines(data):
    groups = defaultdict(list)
    count = len(data.get("text", []))
    for index in range(count):
        word = _clean(data["text"][index])
        if not word:
            continue
        try:
            confidence = float(data.get("conf", ["100"] * count)[index])
        except (TypeError, ValueError):
            confidence = 100
        if confidence < 0:
            continue
        key = tuple(data.get(field, [0] * count)[index] for field in ("block_num", "par_num", "line_num"))
        groups[key].append({"text": word, "left": int(data["left"][index]), "top": int(data["top"][index]), "width": int(data["width"][index]), "height": int(data["height"][index])})
    return [sorted(words, key=lambda word: word["left"]) for words in groups.values()]


def parse_schedule_ocr_data(data):
    """Extract timetable cells using Tesseract word coordinates.

    Course, section and classroom text are intentionally retained together as
    the activity name, which works for both supplied image formats.
    """
    lines = _ocr_lines(data)
    by_day = {}
    for line in lines:
        for word in line:
            day = _is_day(word["text"])
            if day:
                center = word["left"] + word["width"] / 2
                if day not in by_day or word["top"] < by_day[day][2]:
                    by_day[day] = (center, day, word["top"])
    headers = sorted(by_day.values())
    if len(headers) < 2:
        return []

    first_day_left = headers[0][0]
    time_rows = []
    for line in lines:
        match = TIME_RANGE.search(" ".join(word["text"] for word in line))
        if match and min(word["left"] for word in line) < first_day_left - 15:
            time_rows.append((min(word["top"] for word in line), match.group(1), match.group(2)))
    time_rows.sort()
    unique_rows = []
    for row in time_rows:
        if not unique_rows or abs(row[0] - unique_rows[-1][0]) > 4:
            unique_rows.append(row)
    if not unique_rows:
        return []

    row_bounds = []
    for index, (top, start, end) in enumerate(unique_rows):
        next_top = unique_rows[index + 1][0] if index + 1 < len(unique_rows) else top + max(45, top - unique_rows[index - 1][0] if index else 65)
        row_bounds.append((top - 4, next_top - 4, start, end))

    cells = defaultdict(list)
    header_top = min(header[2] for header in headers)
    spacing = (headers[-1][0] - headers[0][0]) / max(1, len(headers) - 1)
    for line in lines:
        for word in line:
            # Header centres can be to the right of a cell's first word.
            if word["top"] <= header_top + 10 or word["left"] + word["width"] < first_day_left - 30:
                continue
            center = word["left"] + word["width"] / 2
            if center < headers[0][0] - spacing / 2 or center > headers[-1][0] + spacing / 2:
                continue
            day = min(headers, key=lambda header: abs(header[0] - center))[1]
            for row_index, (top, bottom, _start, _end) in enumerate(row_bounds):
                if top <= word["top"] < bottom:
                    cells[(row_index, day)].append(word)
                    break

    schedule = []
    for (row_index, day), words in cells.items():
        words.sort(key=lambda word: (word["top"], word["left"]))
        activity = _clean(" ".join(word["text"] for word in words))
        if activity:
            _top, _bottom, start, end = row_bounds[row_index]
            schedule.append({"activity": activity, "day": day, "start": start, "end": end})
    return sorted(schedule, key=lambda row: (row["day"].value, row["start"]))
