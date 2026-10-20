import io
import unittest
from datetime import datetime, time
from unittest.mock import patch

from fastapi import UploadFile
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.main
from app.api.routes.import_routes import _preview, _save_schedule
from app.database.base import Base
from app.models.activity import Activity
from app.models.enums import DayOfWeek
from app.models.person import Person
from app.models.time_block import TimeBlock
from app.services.parsers.value_normalizer import parse_time
from app.services.parsers.ocr_schedule_parser import parse_schedule_text


class ImportAuditTest(unittest.TestCase):
    def test_excel_and_numeric_time_values(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Asignatura", "Día de la semana", "Hora inicial", "Hora final", "Salón"])
        sheet.append(["Cálculo", "Miércoles", 8 / 24, datetime(2026, 1, 1, 9, 30), "B-2"])
        stream = io.BytesIO(); workbook.save(stream)
        preview = _preview(UploadFile(filename="schedule.xlsx", file=io.BytesIO(stream.getvalue())))
        self.assertTrue(preview["success"])
        self.assertEqual(preview["schedule"][0]["day"], DayOfWeek.WEDNESDAY)
        self.assertEqual((preview["schedule"][0]["start"], preview["schedule"][0]["end"]), (time(8), time(9, 30)))
        self.assertEqual(preview["schedule"][0]["room"], "B-2")

    def test_csv_headers_and_twelve_hour_time(self):
        content = "Asignatura,Día de la semana,Hora inicial,Hora final,Salón\nHistoria,Lunes,8:00 AM,09:30 AM,A-1\n".encode()
        preview = _preview(UploadFile(filename="schedule.csv", file=io.BytesIO(content)))
        self.assertTrue(preview["success"])
        self.assertEqual(preview["schedule"][0]["start"], time(8))

    def test_invalid_rows_are_editable_and_not_fabricated(self):
        content = b"Actividad,Dia,Inicio,Fin\nClase,Lunes,10:00,09:00\n"
        preview = _preview(UploadFile(filename="bad.csv", file=io.BytesIO(content)))
        self.assertFalse(preview["success"])
        self.assertEqual(preview["schedule"][0]["start"], "10:00")
        self.assertEqual(preview["errors"][0]["row"], 0)

    def test_pdf_falls_back_from_invalid_tables_to_text(self):
        upload = UploadFile(filename="schedule.pdf", file=io.BytesIO(b"pdf"))
        with patch("app.api.routes.import_routes.extract_tables", return_value=[[['foo'], ['bar']]]), patch("app.api.routes.import_routes.extract_text", return_value="Lunes 08:00-09:00 Historia"):
            preview = _preview(upload)
        self.assertTrue(preview["success"])
        self.assertEqual(preview["schedule"][0]["activity"], "Historia")

    def test_parse_time_supported_values(self):
        self.assertEqual(parse_time("8:05 PM"), time(20, 5))
        self.assertEqual(parse_time(datetime(2026, 1, 1, 7, 20)), time(7, 20))
        self.assertEqual(parse_time(0.5), time(12))
        self.assertEqual(parse_schedule_text("Lunes 08:00 AM-09:00 AM Historia")[0]["start"], "08:00 AM")

    def test_replace_and_duplicate_import_are_transactional(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine); db = Session(engine)
        try:
            person = Person(name="Ana", email="audit@test.local")
            db.add(person); db.flush()
            old = Activity(person_id=person.id_person, name="Vieja", type="IMPORTED")
            db.add(old); db.flush()
            db.add(TimeBlock(activity_id=old.id_activity, day_of_week=DayOfWeek.MONDAY, start_time=time(7), end_time=time(8))); db.commit()
            result = _save_schedule(person.id_person, [{"activity": "Nueva", "day": DayOfWeek.TUESDAY, "start": "09:00", "end": "10:00"}] * 2, True, db)
            self.assertEqual(result["created_blocks"], 1); self.assertEqual(result["skipped_duplicates"], 1)
            self.assertEqual(db.query(TimeBlock).count(), 1)
            with patch("app.api.routes.import_routes.import_schedule", side_effect=RuntimeError("write failed")):
                with self.assertRaises(RuntimeError):
                    _save_schedule(person.id_person, [{"activity": "Falla", "day": DayOfWeek.WEDNESDAY, "start": "09:00", "end": "10:00"}], True, db)
            self.assertEqual(db.query(Activity).filter(Activity.name == "Nueva").count(), 1)
        finally:
            db.close(); Base.metadata.drop_all(engine); engine.dispose()


if __name__ == "__main__":
    unittest.main()
