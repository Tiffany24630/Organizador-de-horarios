import unittest
from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.main
from app.database.base import Base
from app.models.activity import Activity
from app.models.enums import DayOfWeek
from app.models.person import Person
from app.models.time_block import TimeBlock
from app.services.parsers.generic_schedule_parser import parse_dataframe
from app.services.validators.schedule_validator import validate_schedule


class RoomCompatibilityTest(unittest.TestCase):
    def test_import_keeps_optional_room_and_legacy_rows(self):
        parsed = parse_dataframe([
            {"Actividad": "Matemática", "Día": "Lunes", "Inicio": "08:00", "Fin": "08:45", "Aula": "A-201"},
            {"Actividad": "Trabajo", "Día": "Lunes", "Inicio": "09:00", "Fin": "10:00"},
        ])
        self.assertTrue(parsed["success"])
        cleaned = validate_schedule(parsed["schedule"])["cleaned"]
        self.assertEqual(cleaned[0]["room"], "A-201")
        self.assertNotIn("room", cleaned[1])

    def test_room_is_persisted_without_changing_time_block_shape(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        db = Session(engine)
        try:
            person = Person(name="Ana", email="room@test.local")
            db.add(person)
            db.flush()
            activity = Activity(person_id=person.id_person, name="Clase", type="IMPORTED")
            db.add(activity)
            db.flush()
            db.add(TimeBlock(activity_id=activity.id_activity, day_of_week=DayOfWeek.MONDAY, start_time=time(8), end_time=time(9), room="A-201"))
            db.commit()
            stored = db.query(TimeBlock).one()
            self.assertEqual(stored.room, "A-201")
            self.assertEqual((stored.start_time, stored.end_time), (time(8), time(9)))
        finally:
            db.close()
            Base.metadata.drop_all(engine)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
