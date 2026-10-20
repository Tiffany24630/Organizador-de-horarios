import json
from datetime import datetime
from itertools import combinations, product
from math import prod

from sqlalchemy.orm import Session

from app.models.activity_group import ActivityGroup
from app.models.enums import ProposalStatus
from app.models.proposal_attendance import ProposalAttendance
from app.models.proposed_schedule import ProposedSchedule
from app.models.proposed_session import ProposedSession
from app.services.availability_service import get_group_blocks
from app.services.restriction_engine import restriction_reason

DAY_ORDER = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
DAY_START = 6 * 60
DAY_END = 21 * 60
MAX_SEARCH_COMBINATIONS = 1_000_000


def _minutes(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def _clock(total: int) -> str:
    return f"{total // 60:02d}:{total % 60:02d}"


def _time_minutes(value) -> int:
    return value.hour * 60 + value.minute


def _overlap(start, end, busy_start, busy_end):
    return max(0, min(end, busy_end) - max(start, busy_start))


def _session_conflicts(blocks, session):
    start = _minutes(session["start"])
    end = _minutes(session["end"])
    overlaps = []
    intervals = []
    for block in blocks:
        if block.day_of_week.value != session["day"]:
            continue
        busy_start = _time_minutes(block.start_time)
        busy_end = _time_minutes(block.end_time)
        if _overlap(start, end, busy_start, busy_end):
            intervals.append((max(start, busy_start), min(end, busy_end)))
            overlaps.append({
                "activity": block.activity.name if block.activity else "Actividad",
                "day": block.day_of_week.value,
                "start": block.start_time.strftime("%H:%M"),
                "end": block.end_time.strftime("%H:%M"),
            })
    intervals.sort()
    merged = []
    for interval_start, interval_end in intervals:
        if merged and interval_start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], interval_end))
        else:
            merged.append((interval_start, interval_end))
    occupied = sum(interval_end - interval_start for interval_start, interval_end in merged)
    return occupied, overlaps


def _available_minutes(blocks, session: dict) -> int:
    start = _minutes(session["start"])
    end = _minutes(session["end"])
    occupied, _ = _session_conflicts(blocks, session)
    return max(0, end - start - occupied)


def _restriction_allows(group: ActivityGroup, day: str, start: int, end: int) -> bool:
    return restriction_reason(group, day, start, end) is None


def _candidate_sessions(group: ActivityGroup, slot_minutes: int = 5) -> list[dict]:
    candidates = []
    for day in DAY_ORDER:
        for start in range(DAY_START, DAY_END - group.duration_minutes + 1, slot_minutes):
            end = start + group.duration_minutes
            if _restriction_allows(group, day, start, end):
                candidates.append({"day": day, "start": _clock(start), "end": _clock(end)})
    return candidates


def _candidate_combinations(candidates, sessions_per_week):
    by_day = {day: [item for item in candidates if item["day"] == day] for day in DAY_ORDER}
    available_days = [day for day in DAY_ORDER if by_day[day]]
    if sessions_per_week > len(available_days):
        return
    for selected_days in combinations(available_days, sessions_per_week):
        for combo in product(*(by_day[day] for day in selected_days)):
            yield combo


def _evaluate(combo, group, group_blocks, participants, availability_cache):
    attendance = []
    attending_count = 0
    total_available = 0
    conflict_count = 0
    for participant in participants:
        minutes_per_session = []
        session_conflicts = []
        for session in combo:
            available, conflicts = availability_cache[(participant.person_id, session["day"], session["start"], session["end"])]
            minutes_per_session.append(available)
            session_conflicts.append({"session": session, "blocks": conflicts})
            conflict_count += len(conflicts)
        can_attend = all(minutes >= group.minimum_attendance_minutes for minutes in minutes_per_session)
        if can_attend:
            reason = None
        elif any(item["blocks"] for item in session_conflicts):
            reason = f"Conflicto con una actividad existente; se requieren {group.minimum_attendance_minutes} minutos por sesión"
        else:
            reason = f"No alcanza el mínimo de {group.minimum_attendance_minutes} minutos en una o más sesiones"
        if can_attend:
            attending_count += 1
        total_available += sum(minutes_per_session)
        attendance.append({
            "person_id": participant.person_id,
            "name": participant.person.name if participant.person else f"Persona {participant.person_id}",
            "minutes": sum(minutes_per_session),
            "minutes_per_session": minutes_per_session,
            "can_attend": can_attend,
            "reason": reason,
            "conflicts": session_conflicts,
        })
    return {
        "sessions": combo,
        "attendance": attendance,
        "attending_count": attending_count,
        "attendance_percentage": attending_count / len(participants),
        "total_available": total_available,
        "conflict_count": conflict_count,
    }


def _sort_key(item):
    return (-item["attending_count"], -item["total_available"], item["conflict_count"], tuple((s["day"], s["start"]) for s in item["sessions"]))


def generate_proposals(group_id: int, db: Session, slot_minutes: int = 20):
    group = db.get(ActivityGroup, group_id)
    if not group:
        raise ValueError("Group not found")
    participants = list(group.participants)
    if not participants:
        raise ValueError("Group has no participants")
    if not 1 <= group.sessions_per_week <= 7:
        raise ValueError("Sessions per week must be between 1 and 7")
    if group.duration_minutes <= 0 or group.minimum_attendance_minutes <= 0 or group.minimum_attendance_minutes > group.duration_minutes:
        raise ValueError("Invalid duration or minimum attendance")
    if not 1 <= slot_minutes <= 60:
        raise ValueError("slot_minutes must be between 1 and 60")

    candidates = _candidate_sessions(group, slot_minutes)
    group_blocks = get_group_blocks(group_id, db)
    possible_days = len({candidate["day"] for candidate in candidates})
    if group.sessions_per_week > possible_days:
        evaluated = []
    else:
        by_day_counts = [sum(candidate["day"] == day for candidate in candidates) for day in DAY_ORDER if any(candidate["day"] == day for candidate in candidates)]
        candidate_count = sum(prod(selected) for selected in combinations(by_day_counts, group.sessions_per_week))
        if candidate_count > MAX_SEARCH_COMBINATIONS:
            raise ValueError(
                f"La búsqueda produciría {candidate_count} combinaciones; reduce la duración, los días o usa un intervalo mayor ({slot_minutes} minutos). No se devolvieron resultados parciales."
            )
        combinations_to_evaluate = list(_candidate_combinations(candidates, group.sessions_per_week))
        availability_cache = {}
        for participant in participants:
            blocks_for_person = group_blocks.get(participant.person_id, [])
            for candidate in candidates:
                key = (participant.person_id, candidate["day"], candidate["start"], candidate["end"])
                occupied, conflicts = _session_conflicts(blocks_for_person, candidate)
                availability_cache[key] = (group.duration_minutes - occupied, conflicts)
        evaluated = [_evaluate(combo, group, group_blocks, participants, availability_cache) for combo in combinations_to_evaluate]

    if evaluated:
        best_attendance = max(item["attending_count"] for item in evaluated)
        evaluated = [item for item in evaluated if item["attending_count"] == best_attendance]
        evaluated.sort(key=_sort_key)

    for old in db.query(ProposedSchedule).filter(ProposedSchedule.group_id == group_id, ProposedSchedule.status == ProposalStatus.PENDING).all():
        db.delete(old)
    db.flush()

    response = []
    for index, result in enumerate(evaluated, start=1):
        complete = result["attending_count"] == len(participants)
        explanation = (
            "Todas las personas seleccionadas cumplen el mínimo de asistencia en todas las sesiones."
            if complete else
            f"No existe una coincidencia completa; esta alternativa maximiza la asistencia con {result['attending_count']} de {len(participants)} personas."
        )
        proposal = ProposedSchedule(
            group_id=group_id, name=f"Opción {index}", attendance_percentage=result["attendance_percentage"],
            score=float(result["attending_count"]), attending_count=result["attending_count"],
            total_people=len(participants), explanation=explanation, status=ProposalStatus.PENDING,
        )
        db.add(proposal); db.flush()
        for session in result["sessions"]:
            db.add(ProposedSession(schedule_id=proposal.id_schedule, day_of_week=session["day"], start_time=datetime.strptime(session["start"], "%H:%M").time(), end_time=datetime.strptime(session["end"], "%H:%M").time()))
        for item in result["attendance"]:
            db.add(ProposalAttendance(
                proposal_id=proposal.id_schedule, person_id=item["person_id"], can_attend=item["can_attend"],
                available_minutes=item["minutes"], reason=item["reason"], conflicts_json=json.dumps(item["conflicts"]),
            ))
        response.append({
            "proposal_id": proposal.id_schedule, "name": proposal.name, "score": proposal.score,
            "attendance": proposal.attendance_percentage, "attending_count": result["attending_count"],
            "total_people": len(participants), "explanation": explanation,
            "sessions": list(result["sessions"]), "people": result["attendance"],
        })
    db.commit()
    return response
