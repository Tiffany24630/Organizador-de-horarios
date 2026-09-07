from pathlib import Path
from shutil import which

from PIL import Image, ImageEnhance, ImageOps
import pytesseract
from pytesseract import Output, TesseractError, TesseractNotFoundError

LOCAL_TESSDATA = Path(__file__).resolve().parents[2] / "resources" / "tessdata"


def _prepare_image(image_path: str):
    image = Image.open(image_path)
    image = ImageOps.grayscale(image)
    return ImageEnhance.Contrast(image).enhance(1.8)


def _spanish_config():
    """Use the project-local Spanish model when Windows lacks it."""
    if (LOCAL_TESSDATA / "spa.traineddata").exists():
        return f'--tessdata-dir "{LOCAL_TESSDATA}"'
    return ""

def extract_ocr_data_from_image(image_path: str):
    """Get words and coordinates, needed to read timetable columns."""
    if not which("tesseract"):
        common_locations = [
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
        ]
        installed = next((path for path in common_locations if path.exists()), None)
        if installed:
            pytesseract.pytesseract.tesseract_cmd = str(installed)
    try:
        return pytesseract.image_to_data(_prepare_image(image_path), lang="spa", config=_spanish_config(), output_type=Output.DICT)
    except TesseractError:
        return pytesseract.image_to_data(_prepare_image(image_path), output_type=Output.DICT)
    except TesseractNotFoundError as error:
        raise RuntimeError("Tesseract OCR is required to read images") from error


def extract_text_from_image(image_path: str):
    if not which("tesseract"):
        common_locations = [
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
        ]
        installed = next((path for path in common_locations if path.exists()), None)
        if installed:
            pytesseract.pytesseract.tesseract_cmd = str(installed)

    image = _prepare_image(image_path)
    try:
        return pytesseract.image_to_string(image, lang="spa", config=_spanish_config())
    except TesseractError:
        return pytesseract.image_to_string(image)
    except TesseractNotFoundError as error:
        raise RuntimeError(
            "La lectura de imágenes requiere Tesseract OCR instalado en el sistema"
        ) from error
