from app.services.parsers.ocr_schedule_parser import parse_schedule_text

def parse_image_to_schedule(text: str):
    """
    Convierte texto OCR en estructura de horario usable
    """

    schedule = parse_schedule_text(text)

    if not schedule:
        raise ValueError("Could not extract valid schedule from image")

    return schedule