from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
import pandas as pd
import tempfile
from fastapi import Form
from app.services.import_schedule_service import import_schedule
from app.services.parsers.generic_schedule_parser import parse_dataframe

router = APIRouter(prefix="/import", tags=["Import"])

@router.post("/excel")
async def import_excel(file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=f".{suffix}"

    ) as tmp:
        content = await file.read()

        tmp.write(content)

        path = tmp.name

    if suffix.lower() == "csv":
        df = pd.read_csv(path)
        
    else:
        df = pd.read_excel(path)

    return parse_dataframe(df)

@router.post("/excel/save")
async def import_and_save(person_id: int = Form(...), file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1]

    if suffix.lower() == "csv":
        df = pd.read_csv(path)
    
    else:
        df = pd.read_excel(path)

    result = parse_dataframe(df)

    if not result["success"]:
        return result
    
    saved = import_schedule(person_id, result["schedule"], db)

    return {
        "success": True,
        "imported": saved
    }

@router.post("/preview")
async def preview_file(file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1]

    if suffix.lower() == "csv":
        df = pd.read_csv(path)

    else:
        df = pd.read_excel(path)

    result = parse_dataframe(df)

    return result