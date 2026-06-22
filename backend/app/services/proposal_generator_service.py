from sqlalchemy.orm import Session
from app.models.activity_group import ActivityGroup
from app.models.proposed_schedule import ProposedSchedule
from app.models.proposed_session import ProposedSession
from app.services.availability_matrix_service import build_matrix
from app.core.constants import SLOT_MINUTES, MAX_PROPOSALS
from app.utils.time_utils import add_minutes
from datetime import datetime
from datetime import timedelta
from itertools import combinations
from app.models.proposal_attendance import ProposalAttendance
from app.models.proposed_schedule import ProposedSchedule
from app.models.proposed_session import ProposedSession
from app.models.enums import ProposalStatus
from app.utils.time_utils import str_to_time
from app.services.restriction_engine import apply_restrictions
from app.models.space_reservation import SpaceReservation
from app.services.space_engine import apply_space_restrictions
from app.services.attendance_engine import calculate_person_minutes

def build_candidate_sessions(matrix, duration_minutes, minimum_people):
    candidates = []

    slots_needed = duration_minutes // SLOT_MINUTES

    for day in matrix:
        slots = list(matrix[day].keys())

        for i in range(len(slots) - slots_needed + 1):
            valid = True

            values = []

            for j in range(slots_needed):
                slot = slots[i + j]
                availability = matrix[day][slot]

                values.append(availability)

                if (availability < minimum_people):
                    valid = False

            if valid:
                start = slots[i]
                end = add_minutes(start, duration_minutes)

                candidates.append(
                    {
                        "day": day,
                        "start": start,
                        "end": end,
                        "availability": min(values)
                    }
                )

    return candidates

def calculate_score(attendance_percentage, total_available_minutes):
    return attendance_percentage * 100 + total_available_minutes

def explain_conflicts(attendance):
    conflicts = []

    for person in attendance:
        if not person["can_attend"]:
            conflicts.append(person["person_id"])

    return conflicts

def save_attendance(proposal, attendance, db):
    for item in attendance:
        db.add(
            ProposalAttendance(
                proposal_id=proposal.id_schedule,
                person_id=item["person_id"],
                can_attend=item["can_attend"],
                available_minutes=item["minutes"]
            )
        )

def save_proposal(group, pair, attendance_percentage, score, db):
    proposal = ProposedSchedule(
        group_id = group.id_group,
        name = f"Proposal {score}",
        attendance_percentage = attendance_percentage,
        score = score,
        status = ProposalStatus.PENDING
    )

    db.add(proposal)
    db.flush()

    for session in pair:
        db.add(
            ProposedSession(
                schedule_id = proposal.id_schedule,
                day_of_week = session["day"],
                start_time = str_to_time(session["start"]),
                end_time = str_to_time(session["end"])
            )
        )

    return proposal

def build_session_combinations(candidates, sessions_per_week):
    return list(combinations(candidates, sessions_per_week))

def generate_proposals(group_id: int, db: Session):
    group = db.get(ActivityGroup, group_id)

    if not group:
        raise ValueError("Group not found")
    
    if total_people == 0:
        raise ValueError("Group has no participants")
    
    matrix = build_matrix(group_id, db)
    matrix = apply_restrictions(matrix, group)
    reservations = (db.query(SpaceReservation).all())
    matrix = apply_space_restrictions(matrix, reservations)
    total_people = len(group.participants)
    minimum_people = max(1, total_people // 2)
    candidates = build_candidate_sessions(matrix, group.duration_minutes, minimum_people)
    pairs = build_session_combinations(candidates, group.sessions_per_week)

    results = []

    for pair in pairs:
        attendance = []

        valid_people = 0
        total_minutes = 0

        for participant in (group.participants):
            minutes = calculate_person_minutes(participant.person_id, pair, db)
            can_attend = minutes >= group.minimum_attendance_minutes
            
            attendance.append(
                {
                    "person_id": participant.person_id,
                    "minutes": minutes,
                    "can_attend": can_attend
                }
            )

            if can_attend:
                valid_people += 1

            total_minutes += minutes

        attendance_percentage = valid_people / total_people
        score = calculate_score(attendance_percentage, total_minutes)

        results.append(
            {
                "pair": pair,
                "attendance": attendance,
                "attendance_percentage": attendance_percentage,
                "score": score
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:MAX_PROPOSALS]

    response = []

    for result in results:
        proposal = save_proposal(group, result["pair"], result["attendance_percentage"], result["score"], db)
                
        save_attendance(proposal, result["attendance"], db)

        response.append(
            {
                "proposal_id": proposal.id_schedule,
                "score": result["score"],
                "attendance": result["attendance_percentage"]
            }
        )
    
    db.commit()

    return response