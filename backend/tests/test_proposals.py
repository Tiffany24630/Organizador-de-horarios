import unittest
from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.main
from app.database.base import Base
from app.models.activity import Activity
from app.models.activity_group import ActivityGroup
from app.models.enums import DayOfWeek, RestrictionType
from app.models.group_participant import GroupParticipant
from app.models.person import Person
from app.models.restriction import Restriction
from app.models.time_block import TimeBlock
from app.services.proposal_generator_service import generate_proposals
from app.services.proposal_management_service import accept_proposal
from app.api.routes.proposal_routes import get_proposals


class ProposalEngineTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close(); Base.metadata.drop_all(self.engine); self.engine.dispose()

    def people(self, count=2):
        offset = self.db.query(Person).count()
        result = [Person(name=f"Person {offset + index}", email=f"p{offset + index}@test.local") for index in range(count)]
        self.db.add_all(result); self.db.flush()
        return result

    def group(self, people, sessions=1, duration=60, minimum=None):
        group = ActivityGroup(name="Actividad", sessions_per_week=sessions, duration_minutes=duration, minimum_attendance_minutes=minimum or duration)
        self.db.add(group); self.db.flush()
        self.db.add_all([GroupParticipant(group_id=group.id_group, person_id=person.id_person, required=True) for person in people])
        self.db.commit()
        return group

    def busy(self, person, day, start, end, name="Clase"):
        activity = Activity(person_id=person.id_person, name=name, type="MANUAL")
        self.db.add(activity); self.db.flush()
        self.db.add(TimeBlock(activity_id=activity.id_activity, day_of_week=day, start_time=start, end_time=end))
        self.db.commit()

    def allow(self, group, day=None, start=time(8), end=time(10), name="Permitido"):
        self.db.add(Restriction(group_id=group.id_group, name=name, type=RestrictionType.ALLOWED_HOURS, day_of_week=day, start_time=start, end_time=end)); self.db.commit()

    def test_all_attend_and_multiple_complete_options(self):
        group = self.group(self.people(), duration=60); self.allow(group)
        proposals = generate_proposals(group.id_group, self.db, slot_minutes=20)
        self.assertGreater(len(proposals), 1)
        self.assertTrue(all(item["attending_count"] == 2 and item["attendance"] == 1 for item in proposals))

    def test_no_complete_options_returns_all_maximum_attendance(self):
        people = self.people()
        self.busy(people[0], DayOfWeek.MONDAY, time(8), time(9), "Bloque A")
        self.busy(people[1], DayOfWeek.MONDAY, time(9), time(10), "Bloque B")
        group = self.group(people, duration=60); self.allow(group, DayOfWeek.MONDAY)
        self.db.add_all([Restriction(group_id=group.id_group, name=f"No {day.value}", type=RestrictionType.FORBIDDEN_DAY, day_of_week=day) for day in DayOfWeek if day != DayOfWeek.MONDAY]); self.db.commit()
        proposals = generate_proposals(group.id_group, self.db, slot_minutes=60)
        self.assertTrue(proposals)
        self.assertTrue(all(item["attending_count"] == 1 for item in proposals))
        self.assertTrue(any(not person["can_attend"] and person["conflicts"] for person in proposals[0]["people"]))

    def test_overlapping_blocks_are_union_not_double_counted(self):
        person = self.people(1)[0]
        self.busy(person, DayOfWeek.MONDAY, time(8), time(9), "A")
        self.busy(person, DayOfWeek.MONDAY, time(8, 30), time(10), "B")
        group = self.group([person], duration=120); self.allow(group, DayOfWeek.MONDAY, time(8), time(10))
        proposals = generate_proposals(group.id_group, self.db, slot_minutes=60)
        self.assertEqual(proposals[0]["people"][0]["minutes"], 0)
        self.assertEqual(len(proposals[0]["people"][0]["conflicts"][0]["blocks"]), 2)

    def test_partial_conflict_can_attend_when_minimum_is_met(self):
        person = self.people(1)[0]
        self.busy(person, DayOfWeek.MONDAY, time(8), time(8, 15), "Consulta")
        group = self.group([person], duration=60, minimum=40); self.allow(group, DayOfWeek.MONDAY, time(8), time(9))
        proposals = generate_proposals(group.id_group, self.db, slot_minutes=60)
        self.assertTrue(proposals[0]["people"][0]["can_attend"])
        self.assertEqual(proposals[0]["people"][0]["minutes"], 45)

    def test_specific_day_restrictions_and_recurrent_sessions(self):
        group = self.group(self.people(), sessions=2, duration=60)
        self.allow(group, DayOfWeek.MONDAY, time(8), time(9), "Lunes")
        self.allow(group, DayOfWeek.TUESDAY, time(10), time(11), "Martes")
        proposals = generate_proposals(group.id_group, self.db, slot_minutes=60)
        self.assertTrue(proposals)
        self.assertTrue(all({session["day"] for session in proposal["sessions"]} == {"MONDAY", "TUESDAY"} for proposal in proposals))

    def test_no_valid_proposal_and_large_result_are_explicit(self):
        group = self.group(self.people(1), duration=60)
        self.db.add(Restriction(group_id=group.id_group, name="No lunes", type=RestrictionType.FORBIDDEN_DAY, day_of_week=DayOfWeek.MONDAY)); self.db.commit()
        proposals = generate_proposals(group.id_group, self.db, slot_minutes=60)
        self.assertTrue(proposals)  # Other days remain valid.
        group2 = self.group(self.people(1), duration=60)
        many = generate_proposals(group2.id_group, self.db, slot_minutes=60)
        self.assertGreater(len(many), 10)

    def test_no_valid_proposals_returns_empty_without_partial_results(self):
        group = self.group(self.people(1), duration=60)
        self.db.add_all([Restriction(group_id=group.id_group, name=f"Forbidden {day.value}", type=RestrictionType.FORBIDDEN_DAY, day_of_week=day) for day in DayOfWeek]); self.db.commit()
        self.assertEqual(generate_proposals(group.id_group, self.db, slot_minutes=5), [])

    def test_search_limit_returns_explicit_error_without_partial_results(self):
        group = self.group(self.people(1), sessions=2, duration=1, minimum=1)
        with self.assertRaisesRegex(ValueError, "No se devolvieron resultados parciales"):
            generate_proposals(group.id_group, self.db, slot_minutes=1)

    def test_persistence_and_acceptance(self):
        people = self.people()
        group = self.group(people, duration=60); self.allow(group)
        proposals = generate_proposals(group.id_group, self.db, slot_minutes=60)
        stored = self.db.get(type(group.schedules[0]), proposals[0]["proposal_id"])
        accept_proposal(stored, self.db)
        self.assertEqual(stored.status.value, "ACCEPTED")
        self.assertEqual(self.db.query(TimeBlock).count(), 2)

    def test_persisted_proposals_can_be_paged_without_recalculation_or_duplicates(self):
        group = self.group(self.people(), duration=60); self.allow(group)
        generated = generate_proposals(group.id_group, self.db, slot_minutes=60)
        first = get_proposals(group_id=group.id_group, offset=0, limit=2, db=self.db)
        second = get_proposals(group_id=group.id_group, offset=2, limit=2, db=self.db)
        ids = [item["proposal_id"] for item in first["proposals"] + second["proposals"]]
        self.assertEqual(first["total"], len(generated))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [item["proposal_id"] for item in generated[:4]])
        self.assertEqual(first["proposals"][0]["attending_count"], generated[0]["attending_count"])


if __name__ == "__main__":
    unittest.main()
