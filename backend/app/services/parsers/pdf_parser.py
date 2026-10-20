import pdfplumber
from app.services.parsers.image_parser import extract_ocr_data_from_image
from app.services.parsers.ocr_schedule_parser import parse_schedule_ocr_data

def extract_text(pdf_path: str):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_tables(pdf_path: str):
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_tables()

            if extracted:
                tables.extend(extracted)

    return tables


def extract_ocr_schedule(pdf_path: str):
    """Render PDF pages and reuse the timetable OCR parser when text/tables fail."""
    schedule = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            try:
                image = page.to_image(resolution=180).original
                image_path = f"{pdf_path}.page-{page_number}.png"
                image.save(image_path)
                try:
                    schedule.extend(parse_schedule_ocr_data(extract_ocr_data_from_image(image_path)))
                finally:
                    import os
                    if os.path.exists(image_path):
                        os.unlink(image_path)
            except Exception:
                continue
    return schedule
