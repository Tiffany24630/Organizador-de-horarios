from pathlib import Path
from shutil import which

from PIL import Image, ImageEnhance, ImageOps
import pytesseract
from pytesseract import TesseractError, TesseractNotFoundError

def extract_text_from_image(image_path: str):
    if not which("tesseract"):
        common_locations = [
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
        ]
        installed = next((path for path in common_locations if path.exists()), None)
        if installed:
            pytesseract.pytesseract.tesseract_cmd = str(installed)

    image = Image.open(image_path)
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(1.8)
    try:
        return pytesseract.image_to_string(image, lang="spa")
    except TesseractError:
        return pytesseract.image_to_string(image)
    except TesseractNotFoundError as error:
        raise RuntimeError(
            "La lectura de imágenes requiere Tesseract OCR instalado en el sistema"
        ) from error
