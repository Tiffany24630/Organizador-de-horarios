from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.models.time_block import TimeBlock
from app.core.logger import logger
from app.services.parsers.value_normalizer import parse_time

def get_or_create_activity(person_id, activity_name, db):
    activity_name = " ".join(str(activity_name).split())
    activity = db.query(Activity).filter(Activity.person_id == person_id, func.lower(Activity.name) == activity_name.casefold()).first()

    if activity:
        return activity

    activity = Activity(person_id=person_id, name=activity_name, type="IMPORTED")

    db.add(activity)
    db.flush()

    return activity

def import_schedule(person_id, normalized_schedule, db: Session):
    logger.info(f"Importing schedule for person {person_id}")

    created_blocks = 0
    skipped_duplicates = 0
    seen = set()

    for row in normalized_schedule:
        activity = get_or_create_activity(person_id, row["activity"], db)

        start_time = parse_time(row["start"])
        end_time = parse_time(row["end"])

        if start_time >= end_time:
            logger.warning(
                f"Skipping invalid block: "
                f"{row['activity']} "
                f"{start_time} - {end_time}"
            )
            continue

        room = (str(row.get("room")).strip() or None) if row.get("room") is not None else None
        signature = (activity.id_activity, row["day"], start_time, end_time, room)
        if signature in seen or db.query(TimeBlock).filter(
            TimeBlock.activity_id == activity.id_activity,
            TimeBlock.day_of_week == row["day"],
            TimeBlock.start_time == start_time,
            TimeBlock.end_time == end_time,
            TimeBlock.room == room,
        ).first():
            skipped_duplicates += 1
            continue
        seen.add(signature)
        block = TimeBlock(
            activity_id=activity.id_activity,
            day_of_week=row["day"],
            start_time=start_time,
            end_time=end_time,
            room=room,
        )

        db.add(block)

        created_blocks += 1

    logger.info(f"Created {created_blocks} blocks for person {person_id}; skipped {skipped_duplicates} duplicates")

    return {
        "created_blocks": created_blocks
        ,"skipped_duplicates": skipped_duplicates
    }
