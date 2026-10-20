import unittest
from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError

import app.main
from app.database.base import Base
from app.models.activity import Activity
from app.models.enums import DayOfWeek
from app.models.person import Person
from app.models.time_block import TimeBlock
from app.schemas.time_block import TimeBlockEdit
from app.api.routes.time_block_routes import edit_block


class TimeBlockEditTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.person = Person(name='Ana', email='ana-edit@test.local')
        other = Person(name='Luis', email='luis-edit@test.local')
        self.db.add_all([self.person, other])
        self.db.flush()
        self.activity = Activity(person_id=self.person.id_person, name='Matemática', type='MANUAL')
        other_activity = Activity(person_id=other.id_person, name='No tocar', type='MANUAL')
        self.db.add_all([self.activity, other_activity])
        self.db.flush()
        self.block = TimeBlock(activity_id=self.activity.id_activity, day_of_week=DayOfWeek.MONDAY, start_time=time(8), end_time=time(9), room='Aula 1')
        self.other_block = TimeBlock(activity_id=other_activity.id_activity, day_of_week=DayOfWeek.MONDAY, start_time=time(8), end_time=time(9))
        self.db.add_all([self.block, self.other_block])
        self.db.commit()

    def tearDown(self):
        self.db.close(); Base.metadata.drop_all(self.engine); self.engine.dispose()

    def test_edit_persists_activity_block_and_room_without_touching_other_person(self):
        edit_block(self.block.id_block, TimeBlockEdit(activity_name='Física', day_of_week=DayOfWeek.TUESDAY, start_time=time(10), end_time=time(11), room='Lab 2'), self.db)
        self.db.expire_all()
        changed = self.db.get(TimeBlock, self.block.id_block)
        untouched = self.db.get(Activity, self.other_block.activity_id)
        self.assertEqual(changed.day_of_week, DayOfWeek.TUESDAY)
        self.assertEqual((changed.start_time, changed.end_time, changed.room), (time(10), time(11), 'Lab 2'))
        self.assertEqual(self.db.get(Activity, self.activity.id_activity).name, 'Física')
        self.assertEqual(untouched.name, 'No tocar')

    def test_invalid_time_is_rejected_before_persistence(self):
        with self.assertRaises(ValidationError):
            TimeBlockEdit(activity_name='X', day_of_week=DayOfWeek.MONDAY, start_time=time(12), end_time=time(11))
        self.assertEqual(self.db.get(TimeBlock, self.block.id_block).start_time, time(8))


if __name__ == '__main__':
    unittest.main()
