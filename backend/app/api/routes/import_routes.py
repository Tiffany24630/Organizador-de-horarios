import csv
import os
import tempfile
from datetime import time
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from openpyxl import load_workbook
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.enums import DayOfWeek
from app.models.person import Person
from app.services.import_schedule_service import import_schedule
from app.services.parsers.generic_schedule_parser import parse_dataframe
from app.services.parsers.image_parser import extract_ocr_data_from_image, extract_text_from_image
from app.services.parsers.image_schedule_parser import parse_image_to_schedule
from app.services.parsers.ocr_schedule_parser import parse_schedule_ocr_data
from app.services.parsers.pdf_parser import extract_ocr_schedule, extract_tables, extract_text
from app.services.validators.schedule_validator import validate_schedule

router = APIRouter(prefix="/import", tags=["Import"])
SUPPORTED_EXTENSIONS = {"csv", "xlsx", "pdf", "png", "jpg", "jpeg"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


class UploadRejected(ValueError):
    pass


class EditableScheduleRow(BaseModel):
    activity: str = Field(min_length=1, max_length=100)
    day: DayOfWeek
    start: time
    end: time
    room: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def valid_range(self):
        if self.end <= self.start:
            raise ValueError("End time must be after start time")
        return self


class ScheduleImportRequest(BaseModel):
    person_id: int
    schedule: list[EditableScheduleRow]
    replace_existing: bool = False


def _read_upload(file: UploadFile) -> bytes:
    file.file.seek(0)
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    if not content:
        raise UploadRejected("El archivo está vacío")
    if len(content) > MAX_UPLOAD_BYTES:
        raise UploadRejected("El archivo supera el límite de 20 MB")
    return content


def _read_csv(path: str):
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8-sig", errors="replace")
    if not text.strip():
        raise UploadRejected("El archivo CSV está vacío")
    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(text.splitlines(), dialect=dialect))


def _rows_from_tables(tables):
    rows = []
    for table in tables or []:
        if not table or len(table) < 2:
            continue
        headers = [str(value or "").strip() for value in table[0]]
        for values in table[1:]:
            if values and any(value not in (None, "") for value in values):
                rows.append(dict(zip(headers, values)))
    return rows


def _parse_loaded(loaded):
    if isinstance(loaded, list) and loaded and set(loaded[0]).issuperset({"activity", "day", "start", "end"}):
        return {"success": True, "schedule": loaded}
    return parse_dataframe(loaded)


def _has_valid_schedule(rows):
    return bool(rows) and validate_schedule(rows)["valid"]


def load_dataframe(file: UploadFile):
    suffix = Path(file.filename or "").suffix.lower().lstrip(".")
    if suffix not in SUPPORTED_EXTENSIONS:
        if suffix == "xls":
            raise ValueError("Los archivos .xls no están disponibles: instale xlrd para habilitarlos")
        raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")

    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as temporary:
            temporary.write(_read_upload(file))
            path = temporary.name

        if suffix == "csv":
            return _read_csv(path)
        if suffix == "xlsx":
            workbook = load_workbook(path, read_only=True, data_only=True)
            try:
                sheet = workbook.active
                values = list(sheet.iter_rows(values_only=True))
            finally:
                workbook.close()
            if not values:
                raise UploadRejected("El archivo Excel no contiene filas")
            headers = [str(value or "").strip() for value in values[0]]
            return [dict(zip(headers, row)) for row in values[1:] if any(value is not None for value in row)]
        if suffix == "pdf":
            table_rows = _rows_from_tables(extract_tables(path))
            if _has_valid_schedule(table_rows):
                return table_rows
            pdf_text = extract_text(path)
            try:
                text_rows = parse_image_to_schedule(pdf_text) if pdf_text.strip() else []
            except ValueError:
                text_rows = []
            if _has_valid_schedule(text_rows):
                return text_rows
            ocr_rows = extract_ocr_schedule(path)
            return ocr_rows or text_rows or table_rows

        try:
            rows = parse_schedule_ocr_data(extract_ocr_data_from_image(path))
        except Exception:
            rows = []
        if rows:
            return rows
        text = extract_text_from_image(path)
        return parse_image_to_schedule(text) if text.strip() else []
    finally:
        if path and os.path.exists(path):
            os.unlink(path)


def _preview(file: UploadFile):
    suffix = Path(file.filename or "").suffix.lower()
    try:
        loaded = load_dataframe(file)
        result = _parse_loaded(loaded)
        if not result["success"]:
            return {"success": False, "schedule": [], "errors": [{"type": "HEADER_ERROR", "row": None, "message": result["error"]}], "manual_review": True}
        validation = validate_schedule(result["schedule"])
        return {
            "success": validation["valid"],
            "schedule": validation["editable"],
            "errors": validation["errors"],
            "manual_review": not validation["valid"] or not validation["cleaned"],
        }
    except UploadRejected as error:
        raise HTTPException(413 if "límite" in str(error) else 422, str(error)) from error
    except Exception as error:
        if suffix in {".png", ".jpg", ".jpeg", ".pdf"}:
            return {
                "success": False,
                "schedule": [],
                "errors": [{"type": "OCR_MANUAL_REVIEW", "row": None, "message": f"No se pudo reconocer el horario: {error}. Introduce las filas manualmente."}],
                "manual_review": True,
            }
        raise HTTPException(422, f"No se pudo interpretar el archivo: {error}") from error


def _save_schedule(person_id, rows, replace_existing, db):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    if not rows:
        raise HTTPException(422, "No hay filas válidas para guardar")
    try:
        if replace_existing:
            for activity in list(person.activities):
                db.delete(activity)
            db.flush()
        imported = import_schedule(person_id, rows, db)
        db.commit()
        return imported
    except Exception:
        db.rollback()
        raise


@router.post("/excel")
async def import_excel(file: UploadFile = File(...)):
    return _preview(file)


@router.post("/preview")
async def preview_file(file: UploadFile = File(...)):
    return _preview(file)


@router.post("/save")
def save_edited_schedule(payload: ScheduleImportRequest, db: Session = Depends(get_db)):
    rows = [row.model_dump() for row in payload.schedule]
    return {"success": True, "imported": _save_schedule(payload.person_id, rows, payload.replace_existing, db)}


@router.post("/excel/save")
async def import_and_save(person_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    preview = _preview(file)
    if not preview["success"]:
        return preview
    return {"success": True, "imported": _save_schedule(person_id, preview["schedule"], False, db)}
