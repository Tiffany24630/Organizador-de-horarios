import unittest
import io
from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi import UploadFile

import app.main  # Registers every mapped model before creating the test schema.
from app.database.base import Base
from app.models.activity import Activity
from app.models.activity_group import ActivityGroup
from app.models.enums import DayOfWeek, RestrictionType
from app.models.group_participant import GroupParticipant
from app.models.person import Person
from app.models.proposed_schedule import ProposedSchedule
from app.models.time_block import TimeBlock
from app.models.restriction import Restriction
from app.services.parsers.generic_schedule_parser import parse_dataframe
from app.services.parsers.ocr_schedule_parser import parse_schedule_ocr_data
from app.services.proposal_generator_service import generate_proposals
from app.services.proposal_management_service import accept_proposal
from app.services.validators.schedule_validator import validate_schedule
from app.api.routes.import_routes import _preview


class CompleteWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_import_generate_and_accept(self):
        ana = Person(name="Ana", email="ana@test.local")
        luis = Person(name="Luis", email="luis@test.local")
        self.db.add_all([ana, luis])
        self.db.flush()

        parsed = parse_dataframe([
            {"Actividad": "Trabajo", "Día": "Lunes", "Inicio": "13:00", "Fin": "14:00"},
        ])
        self.assertTrue(parsed["success"])
        self.assertTrue(validate_schedule(parsed["schedule"])["valid"])

        busy = Activity(person_id=ana.id_person, name="Trabajo", type="MANUAL")
        self.db.add(busy)
        self.db.flush()
        self.db.add(TimeBlock(
            activity_id=busy.id_activity,
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(13, 0),
            end_time=time(14, 0),
        ))
        group = ActivityGroup(
            name="Ensayo",
            sessions_per_week=2,
            duration_minutes=80,
            minimum_attendance_minutes=40,
        )
        self.db.add(group)
        self.db.flush()
        self.db.add_all([
            GroupParticipant(group_id=group.id_group, person_id=ana.id_person, required=True),
            GroupParticipant(group_id=group.id_group, person_id=luis.id_person, required=True),
            Restriction(group_id=group.id_group, name="Rango diario", type=RestrictionType.ALLOWED_HOURS, start_time=time(15, 0), end_time=time(20, 0)),
        ])
        self.db.commit()

        options = generate_proposals(group.id_group, self.db)
        self.assertGreater(len(options), 0)
        self.assertEqual(len(options[0]["sessions"]), 2)
        self.assertEqual(len({item["day"] for item in options[0]["sessions"]}), 2)
        self.assertEqual(len(options[0]["people"]), 2)
        self.assertTrue(all(item["start"] >= "15:00" and item["end"] <= "20:00" for item in options[0]["sessions"]))

        proposal = self.db.get(ProposedSchedule, options[0]["proposal_id"])
        accept_proposal(proposal, self.db)
        events = self.db.query(Activity).filter(Activity.type == "GROUP_EVENT").all()
        self.assertEqual(len(events), 2)
        self.assertTrue(all(len(event.time_blocks) == 2 for event in events))

    def test_image_without_ocr_opens_manual_editor(self):
        upload = UploadFile(filename="horario.png", file=io.BytesIO(b"invalid image"))
        preview = _preview(upload)
        self.assertFalse(preview["success"])
        self.assertEqual(preview["errors"][0]["type"], "OCR_MANUAL_REVIEW")
        self.assertEqual(len(preview["schedule"]), 1)

    def test_semicolon_csv_upload_is_parsed(self):
        content = "Actividad;Día;Inicio;Fin\nTrabajo;Lunes;08:00;09:00\n".encode()
        upload = UploadFile(filename="horario.csv", file=io.BytesIO(content))
        preview = _preview(upload)

        self.assertTrue(preview["success"])
        self.assertEqual(preview["schedule"][0]["activity"], "Trabajo")
        self.assertEqual(preview["schedule"][0]["day"], DayOfWeek.MONDAY)

    def test_scanned_pdf_opens_manual_editor(self):
        upload = UploadFile(filename="horario.pdf", file=io.BytesIO(b"invalid pdf"))
        preview = _preview(upload)

        self.assertFalse(preview["success"])
        self.assertEqual(preview["errors"][0]["type"], "OCR_MANUAL_REVIEW")

    def test_ocr_table_preserves_day_time_and_cell_contents(self):
        words = [
            ("Hora", 20, 20), ("Lun", 150, 20), ("Mar", 300, 20),
            ("07:00", 20, 70), ("-", 64, 70), ("07:45", 76, 70),
            ("CC3054", 140, 70), ("-", 195, 70), ("Sección:", 140, 92), ("41", 210, 92), ("Aula:", 140, 114), ("CIT-639", 185, 114),
            ("CC2008", 300, 70), ("-", 355, 70), ("Sección:", 300, 92), ("41", 370, 92),
            ("07:50", 20, 145), ("-", 64, 145), ("08:35", 76, 145),
        ]
        data = {key: [] for key in ("text", "left", "top", "width", "height", "conf", "block_num", "par_num", "line_num")}
        for index, (text, left, top) in enumerate(words):
            data["text"].append(text); data["left"].append(left); data["top"].append(top)
            data["width"].append(max(8, len(text) * 7)); data["height"].append(12); data["conf"].append("95")
            data["block_num"].append(1); data["par_num"].append(top); data["line_num"].append(1)
        schedule = parse_schedule_ocr_data(data)
        monday = next(row for row in schedule if row["day"] == DayOfWeek.MONDAY)
        self.assertEqual((monday["start"], monday["end"]), ("07:00", "07:45"))
        self.assertIn("CC3054", monday["activity"])
        self.assertIn("CIT-639", monday["activity"])


if __name__ == "__main__":
    unittest.main()
