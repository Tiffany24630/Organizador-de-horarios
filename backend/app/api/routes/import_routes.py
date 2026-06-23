from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.import_schedule_service import import_schedule
from app.services.parsers.generic_schedule_parser import parse_dataframe
import pandas as pd
import tempfile

router = APIRouter(prefix="/import", tags=["Import"])

def load_dataframe(file: UploadFile):
    suffix = file.filename.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        content = file.file.read()
        tmp.write(content)
        path = tmp.name

    if suffix == "csv":
        return pd.read_csv(path)

    return pd.read_excel(path)

@router.post("/excel")
async def import_excel(file: UploadFile = File(...)):
    df = load_dataframe(file)
    return parse_dataframe(df)

@router.post("/preview")
async def preview_file(file: UploadFile = File(...)):
    df = load_dataframe(file)
    return parse_dataframe(df)

@router.post("/excel/save")
async def import_and_save(person_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = load_dataframe(file)

    result = parse_dataframe(df)

    if not result["success"]:
        return result

    saved = import_schedule(person_id, result["schedule"], db)

    return {
        "success": True,
        "imported": saved
    }