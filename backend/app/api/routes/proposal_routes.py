import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.proposed_schedule import ProposedSchedule
from app.services.proposal_generator_service import generate_proposals
from app.services.proposal_management_service import accept_proposal, reject_proposal

router = APIRouter(prefix="/proposals", tags=["Proposals"])


def _attendance(item):
    return {
        "person_id": item.person_id,
        "name": item.person.name if item.person else f"Persona {item.person_id}",
        "can_attend": item.can_attend,
        "available_minutes": item.available_minutes,
        "reason": item.reason,
        "conflicts": json.loads(item.conflicts_json or "[]"),
    }


def _serialize(proposal):
    return {
        "proposal_id": proposal.id_schedule,
        "name": proposal.name,
        "group_id": proposal.group_id,
        "score": proposal.score,
        "attendance": proposal.attendance_percentage,
        "attending_count": proposal.attending_count,
        "total_people": proposal.total_people,
        "explanation": proposal.explanation,
        "status": proposal.status,
        "sessions": [{"day": item.day_of_week.value, "start": item.start_time.strftime("%H:%M"), "end": item.end_time.strftime("%H:%M")} for item in proposal.sessions],
        "people": [_attendance(item) for item in proposal.attendances],
    }


@router.post("/generate/{group_id}")
def generate(group_id: int, slot_minutes: int = Query(20, ge=1, le=60), offset: int = Query(0, ge=0), limit: int | None = Query(None, ge=1, le=500), db: Session = Depends(get_db)):
    try:
        proposals = generate_proposals(group_id, db, slot_minutes=slot_minutes)
        if limit is not None:
            return {"proposals": proposals[offset:offset + limit], "total": len(proposals), "offset": offset, "limit": limit}
        return proposals
    except ValueError as error:
        raise HTTPException(400, str(error)) from error


@router.put("/{proposal_id}/accept")
def accept(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    try:
        accept_proposal(proposal, db)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(400, f"No se pudo aceptar la propuesta: {error}") from error
    return {"message": "Proposal accepted", "proposal": _serialize(proposal)}


@router.get("/")
def get_proposals(group_id: int | None = Query(None, ge=1), offset: int = Query(0, ge=0), limit: int | None = Query(None, ge=1, le=500), db: Session = Depends(get_db)):
    query = db.query(ProposedSchedule).order_by(ProposedSchedule.score.desc(), ProposedSchedule.id_schedule)
    if group_id is not None:
        query = query.filter(ProposedSchedule.group_id == group_id)
    total = query.count()
    items = query.offset(offset).limit(limit).all() if limit is not None else query.all()
    serialized = [_serialize(item) for item in items]
    return {"proposals": serialized, "total": total, "offset": offset, "limit": limit} if limit is not None else serialized


@router.get("/{proposal_id}")
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    return _serialize(proposal)


@router.put("/{proposal_id}/reject")
def reject(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.get(ProposedSchedule, proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    reject_proposal(proposal, db)
    db.commit()
    return {"message": "Proposal rejected"}
