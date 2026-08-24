from datetime import datetime
from itertools import combinations, product

from sqlalchemy.orm import Session

from app.core.constants import DAY_END, DAY_START, MAX_PROPOSALS, SLOT_MINUTES
from app.models.activity_group import ActivityGroup
from app.models.enums import ProposalStatus
from app.models.proposal_attendance import ProposalAttendance
from app.models.proposed_schedule import ProposedSchedule
from app.models.proposed_session import ProposedSession
from app.services.availability_service import get_group_blocks


def _minutes(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def _clock(total: int) -> str:
    return f"{total // 60:02d}:{total % 60:02d}"


def _overlap(start: int, end: int, busy_start: int, busy_end: int) -> int:
    return max(0, min(end, busy_end) - max(start, busy_start))


def _available_minutes(blocks, session: dict) -> int:
    start = _minutes(session["start"])
    end = _minutes(session["end"])
    occupied = 0
    for block in blocks:
        if block.day_of_week.value != session["day"]:
            continue
        busy_start = block.start_time.hour * 60 + block.start_time.minute
        busy_end = block.end_time.hour * 60 + block.end_time.minute
        occupied += _overlap(start, end, busy_start, busy_end)
    return max(0, end - start - min(end - start, occupied))


def _restriction_allows(group: ActivityGroup, day: str, start: int, end: int) -> bool:
    for restriction in group.restrictions:
        kind = restriction.type.value
        restriction_day = restriction.day_of_week.value if restriction.day_of_week else None
        if kind == "FORBIDDEN_DAY" and restriction_day == day:
            return False
        if restriction_day and restriction_day != day:
            continue
        if restriction.start_time is None or restriction.end_time is None:
            continue
        restricted_start = restriction.start_time.hour * 60 + restriction.start_time.minute
        restricted_end = restriction.end_time.hour * 60 + restriction.end_time.minute
        if kind == "ALLOWED_HOURS" and (start < restricted_start or end > restricted_end):
            return False
        if kind == "FORBIDDEN_HOURS" and _overlap(start, end, restricted_start, restricted_end):
            return False
    return True


def _candidate_sessions(group: ActivityGroup, group_blocks: dict, people: list[int]) -> list[dict]:
    candidates = []
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    for day in days:
        for start in range(_minutes(DAY_START), _minutes(DAY_END) - group.duration_minutes + 1, SLOT_MINUTES):
            end = start + group.duration_minutes
            if not _restriction_allows(group, day, start, end):
                continue
            session = {"day": day, "start": _clock(start), "end": _clock(end)}
            available = [_available_minutes(group_blocks.get(person_id, []), session) for person_id in people]
            eligible = sum(value >= group.minimum_attendance_minutes for value in available)
            candidates.append({**session, "eligible": eligible, "total_minutes": sum(available)})

    shortlist = []
    for day in days:
        day_items = [item for item in candidates if item["day"] == day]
        day_items.sort(key=lambda item: (item["eligible"], item["total_minutes"]), reverse=True)
        shortlist.extend(day_items[:3])
    return shortlist


def _evaluate(combo, group: ActivityGroup, group_blocks: dict, participants) -> dict:
    attendance = []
    eligible_count = 0
    total_available = 0
    for participant in participants:
        per_session = [_available_minutes(group_blocks.get(participant.person_id, []), session) for session in combo]
        can_attend = all(value >= group.minimum_attendance_minutes for value in per_session)
        attendance.append({"person_id": participant.person_id, "minutes": sum(per_session), "minutes_per_session": per_session, "can_attend": can_attend})
        eligible_count += int(can_attend)
        total_available += sum(per_session)

    required_missing = sum(1 for item, participant in zip(attendance, participants) if participant.required and not item["can_attend"])
    ratio = eligible_count / len(participants)
    score = ratio * 100 + total_available / max(1, len(participants) * group.sessions_per_week * 10) - required_missing * 25
    return {"sessions": combo, "attendance": attendance, "attendance_percentage": ratio, "score": round(score, 2)}


def generate_proposals(group_id: int, db: Session):
    group = db.get(ActivityGroup, group_id)
    if not group:
        raise ValueError("Group not found")
    participants = list(group.participants)
    if not participants:
        raise ValueError("Group has no participants")
    if group.sessions_per_week > 7:
        raise ValueError("Sessions per week cannot exceed 7")
    if group.minimum_attendance_minutes > group.duration_minutes:
        raise ValueError("Minimum attendance cannot exceed session duration")

    people = [participant.person_id for participant in participants]
    blocks = get_group_blocks(group_id, db)
    candidates = _candidate_sessions(group, blocks, people)
    candidates_by_day = {
        day: [item for item in candidates if item["day"] == day]
        for day in {item["day"] for item in candidates}
    }
    combos = []
    for selected_days in combinations(candidates_by_day, group.sessions_per_week):
        combos.extend(product(*(candidates_by_day[day] for day in selected_days)))
    evaluated = [_evaluate(combo, group, blocks, participants) for combo in combos]
    evaluated.sort(key=lambda item: item["score"], reverse=True)
    evaluated = evaluated[:MAX_PROPOSALS]

    for old in db.query(ProposedSchedule).filter(ProposedSchedule.group_id == group_id, ProposedSchedule.status == ProposalStatus.PENDING).all():
        db.delete(old)
    db.flush()

    response = []
    for index, result in enumerate(evaluated, start=1):
        proposal = ProposedSchedule(group_id=group_id, name=f"Opción {index}", attendance_percentage=result["attendance_percentage"], score=result["score"], status=ProposalStatus.PENDING)
        db.add(proposal)
        db.flush()
        for session in result["sessions"]:
            db.add(ProposedSession(schedule_id=proposal.id_schedule, day_of_week=session["day"], start_time=datetime.strptime(session["start"], "%H:%M").time(), end_time=datetime.strptime(session["end"], "%H:%M").time()))
        for item in result["attendance"]:
            db.add(ProposalAttendance(proposal_id=proposal.id_schedule, person_id=item["person_id"], can_attend=item["can_attend"], available_minutes=item["minutes"]))
        response.append({
            "proposal_id": proposal.id_schedule,
            "name": proposal.name,
            "score": proposal.score,
            "attendance": proposal.attendance_percentage,
            "sessions": [{key: value for key, value in session.items() if key in ("day", "start", "end")} for session in result["sessions"]],
            "people": result["attendance"],
        })
    db.commit()
    return response
