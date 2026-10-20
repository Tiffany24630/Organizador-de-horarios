import csv
from pathlib import Path

from openpyxl import load_workbook


def read_excel(file_path: str):
    suffix = Path(file_path).suffix.lower()
    if suffix == ".xls":
        raise ValueError("Los archivos .xls requieren xlrd; no está instalado en esta distribución")
    workbook = load_workbook(file_path, read_only=True, data_only=True)
    try:
        values = list(workbook.active.iter_rows(values_only=True))
    finally:
        workbook.close()
    if not values:
        return []
    headers = [str(value or "").strip() for value in values[0]]
    return [dict(zip(headers, row)) for row in values[1:] if any(value is not None for value in row)]


def read_csv(file_path: str):
    raw = Path(file_path).read_bytes().decode("utf-8-sig", errors="replace")
    if not raw.strip():
        return []
    try:
        dialect = csv.Sniffer().sniff(raw[:8192], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(raw.splitlines(), dialect=dialect))


def dataframe_to_dict(df):
    if isinstance(df, list):
        return df
    return df.to_dict(orient="records")
