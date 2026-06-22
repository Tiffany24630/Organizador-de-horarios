from datetime import datetime
from app.services.availability_service import get_busy_blocks

def overlap_minutes(start1, end1, start2, end2):
    start = max(start1, start2)
    end = min(end1, end2)
    overlap = (end - start).total_seconds() / 60

    return max(0, int(overlap))

def calculate_person_minutes(person_id, sessions, db):
    busy_blocks = get_busy_blocks(person_id, db)
    available = 0

    for session in sessions:
        session_start = datetime.strptime(session["start"], "%H:%M")
        session_end = datetime.strptime(session["end"], "%H:%M")
        duration = int((session_end - session_start).total_seconds() / 60)
        occupied = 0

        for block in busy_blocks:
            if (block.day_of_week.value != session["day"]):
                continue

            block_start = datetime.strptime(block.start_time.strftime("%H:%M"), "%H:%M")
            block_end = datetime.strptime(block.end_time.strftime("%H:%M"), "%H:%M")

            occupied += overlap_minutes(
                session_start,
                session_end,
                block_start,
                block_end
            )

        available += max(0, duration - occupied)

    return available

