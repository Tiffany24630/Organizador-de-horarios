import os

from app.services.parsers.excel_parser import read_csv, read_excel
from app.services.parsers.image_parser import extract_text_from_image
from app.services.parsers.image_schedule_parser import parse_image_to_schedule
from app.services.parsers.ocr_schedule_parser import parse_schedule_text
from app.services.parsers.pdf_parser import extract_ocr_schedule, extract_tables, extract_text
from app.services.parsers.schedule_detector import detect_schedule_from_table


def import_schedule(file_path: str):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".xlsx":
        return read_excel(file_path)
    if extension == ".csv":
        return read_csv(file_path)
    if extension == ".pdf":
        tables = extract_tables(file_path)
        schedule = [item for table in tables for item in detect_schedule_from_table(table)]
        if schedule:
            return schedule
        text = extract_text(file_path)
        if text.strip():
            try:
                schedule = parse_schedule_text(text)
            except Exception:
                schedule = []
        return schedule or extract_ocr_schedule(file_path)
    if extension in {".png", ".jpg", ".jpeg"}:
        try:
            text = extract_text_from_image(file_path)
            return parse_image_to_schedule(text)
        except Exception as error:
            raise ValueError(f"No se pudo reconocer la imagen: {error}") from error
    raise ValueError("Unsupported file type")
