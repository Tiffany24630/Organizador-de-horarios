from datetime import datetime
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.time_block import TimeBlock

def parse_time(value):
    if hasattr(value, "time"):
        return value.time()

    formats = [
        "%H:%M",
        "%H:%M:%S",
        "%I:%M %p"
    ]

    value = str(value).strip()

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()

        except Exception:
            pass

    raise ValueError(f"Invalid time: {value}")

def get_or_create_activity(person_id, activity_name, db):
    activity = db.query(Activity).filter(Activity.person_id == person_id, Activity.name == activity_name).first()

    if activity:
        return activity

    activity = Activity(person_id=person_id, name=activity_name, type="IMPORTED")

    db.add(activity)
    db.flush()

    return activity

def import_schedule( person_id, normalized_schedule, db: Session):
    created_blocks = 0

    for row in normalized_schedule:
        activity = get_or_create_activity(person_id, row["activity"], db)

        block = TimeBlock(
            activity_id=activity.id_activity,
            day_of_week=row["day"],
            start_time=parse_time(row["start"]),
            end_time=parse_time(row["end"])
        )

        db.add(block)

        created_blocks += 1

    db.commit()

    return {
        "created_blocks": created_blocks
    }