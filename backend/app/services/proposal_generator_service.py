from sqlalchemy.orm import Session
from app.models.activity_group import ActivityGroup
from app.models.proposed_schedule import ProposedSchedule
from app.models.proposed_session import ProposedSession
from app.services.availability_matrix_service import (build_matrix)
from app.core.constants import (SLOT_MINUTES, MAX_PROPOSALS)
from datetime import datetime
from datetime import timedelta

def slots_needed(duration_minutes: int):
    return (
        duration_minutes + SLOT_MINUTES - 1
    ) // SLOT_MINUTES

def find_candidate_slots(matrix, people_count, slots_required):
    candidates = []

    for day in matrix:
        times = list(matrix[day].keys())

        for i in range(len(times)):
            score = 0
            valid = True

            for j in range(slots_required):
                if i + j >= len(times):
                    valid = False
                    break

                current = times[i + j]
                available = matrix[day][current]

                if available == 0:
                    valid = False
                    break

                score += available

            if valid:
                attendance = (score / (slots_required * people_count)) * 100

                candidates.append(
                    {
                        "day": day,
                        "start": times[i],
                        "score": score,
                        "attendance": attendance
                    }
                )

    return sorted(
        candidates,
        key=lambda x: (x["attendance"], x["score"]),
        reverse=True
    )

def create_proposal(group, candidate, db):
    schedule = ProposedSchedule(
        group_id = group.id_group,
        name = f"Proposal {candidate['day']}",
        attendance_percentage = candidate["attendance"],
        score=candidate["score"]
    )

    db.add(schedule)
    db.flush()