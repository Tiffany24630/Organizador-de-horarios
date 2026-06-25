import os
from app.services.parsers.excel_parser import read_excel, read_csv
from app.services.parsers.pdf_parser import extract_tables
from app.services.parsers.schedule_detector import detect_schedule_from_table
from app.services.parsers.ocr_schedule_parser import parse_schedule_text
from app.services.parsers.image_parser import extract_text_from_image

def import_schedule(file_path: str):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".xlsx":
        return read_excel(file_path)

    if extension == ".csv":
        return read_csv(file_path)

    if extension == ".pdf":
        tables = extract_tables(file_path)

        schedule = []

        for table in tables:
            schedule.extend(detect_schedule_from_table(table))

        return schedule

    if extension in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(file_path)

        return parse_schedule_text(text)

    raise ValueError("Unsupported file type")