from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.activity_group import ActivityGroup
from app.models.group_participant import GroupParticipant
from app.models.time_block import TimeBlock


def get_group_people(group_id: int, db: Session):
    return [row.person_id for row in db.query(GroupParticipant).filter(GroupParticipant.group_id == group_id).all()]


def get_busy_blocks(person_id: int, db: Session):
    return (
        db.query(TimeBlock)
        .join(Activity, Activity.id_activity == TimeBlock.activity_id)
        .filter(Activity.person_id == person_id)
        .order_by(TimeBlock.day_of_week, TimeBlock.start_time)
        .all()
    )


def build_group_availability(group_id: int, db: Session):
    return {person_id: get_busy_blocks(person_id, db) for person_id in get_group_people(group_id, db)}


def get_group_blocks(group_id: int, db: Session):
    rows = (
        db.query(GroupParticipant.person_id, TimeBlock)
        .join(Activity, Activity.person_id == GroupParticipant.person_id)
        .join(TimeBlock, TimeBlock.activity_id == Activity.id_activity)
        .filter(GroupParticipant.group_id == group_id)
        .order_by(GroupParticipant.person_id, TimeBlock.day_of_week, TimeBlock.start_time)
        .all()
    )
    result = {}
    for person_id, block in rows:
        result.setdefault(person_id, []).append(block)
    return result
