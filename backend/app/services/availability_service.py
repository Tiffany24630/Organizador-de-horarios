from sqlalchemy.orm import Session
from app.models.activity_group import ActivityGroup
from app.models.group_participant import GroupParticipant
from app.models.activity import Activity
from app.models.time_block import TimeBlock
from app.models.group_participant import GroupParticipant
from app.models.activity import Activity
from app.models.time_block import TimeBlock

def get_group_people(group_id: int, db: Session):
    participants = (db.query(GroupParticipant).filter(GroupParticipant.group_id == group_id).all())

    return [p.person_id for p in participants]

def get_busy_blocks(person_id: int, db: Session):
    activities = (db.query(Activity).filter(Activity.person_id == person_id).all())

    result = []

    activities_ids = [
        a.id_activity
        for a in activities
    ]

    blocks = db.query(TimeBlock).filter(TimeBlock.activity_id.in_(activities_ids)).all()

    return blocks

def build_group_availability(group_id: int, db: Session):
    people = get_group_people(group_id, db)

    availability = {}

    for person_id in people:
        busy = get_busy_blocks(person_id, db)

        availability[person_id] = busy

    return availability

def get_group_blocks(group_id: int, db: Session):
    rows = (
        db.query(GroupParticipant.person_id, TimeBlock)
        .join(Activity, Activity.person_id == GroupParticipant.person_id)
        .join(TimeBlock, TimeBlock.activity_id == Activity.id_activity)
        .filter(GroupParticipant.group_id == group_id).all()
    )

    result = {}

    for person_id, block in rows:
        if person_id not in result:
            result[person_id] = []

        result[person_id].append(block)

    return result