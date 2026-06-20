from sqlalchemy.orm import Session
from app.models.activity_group import ActivityGroup
from app.models.group_participant import GroupParticipant
from app.models.activity import Activity
from app.models.time_block import TimeBlock

def get_group_people(group_id: int, db: Session):
    participants = (db.query(GroupParticipant).filter(GroupParticipant.group_id == group_id).all())

    return [p.person_id for p in participants]

def get_busy_blocks(person_id: int, db: Session):
    activities = (db.query(Activity).filter(Activity.person_id == person_id).all())

    result = []

    for activity in activities:
        blocks = (db.query(TimeBlock).filter(TimeBlock.activity_id == activity.id_activity).all())

        result.extend(blocks)

    return result

def build_group_availability(group_id: int, db: Session):
    people = get_group_people(group_id, db)

    availability = {}

    for person_id in people:
        busy = get_busy_blocks(person_id, db)

        availability[person_id] = busy

    return availability

