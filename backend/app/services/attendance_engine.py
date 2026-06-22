from app.models.group_participant import GroupParticipant
from app.services.availability_service import (get_busy_blocks)

def calculate_attendance(group, day, start_time, end_time, db):
    participants = group.participants
    attendance = []
    total_available = 0

    for participant in participants:
        person_id = participant.person_id
        blocks = get_busy_blocks(person_id, db)

        conflict = False

        for block in blocks:
            if (block.day_of_week.value != day):
                continue

            block_start = block.start_time.strftime("%H:%M")
            block_end = block.end_time.strftime("%H:%M")

            if (start_time < block_end and end_time > block_start):
                conflict = True
                break

        attendance.append(
            {
                "person_id": person_id,
                "can_attend": not conflict
            }
        )

        if not conflict:
            total_available += 1

    return attendance, total_available