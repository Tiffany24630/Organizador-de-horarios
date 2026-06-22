from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.connection import get_db
from app.models.group_participant import GroupParticipant
from app.schemas.group_participant import GroupParticipantCreate, GroupParticipantResponse

router = APIRouter(prefix="/group-participants", tags=["Group Participants"])

@router.post("/", response_model=GroupParticipantResponse)
def create_participant(data: GroupParticipantCreate, db: Session = Depends(get_db)):
    participant = GroupParticipant(**data.model_dump())

    db.add(participant)
    db.commit()
    db.refresh(participant)

    return participant

@router.get("/",response_model=list[GroupParticipantResponse])
def get_participants(db: Session = Depends(get_db)):
    return db.query(GroupParticipant).all()

@router.get("/{group_id}")
def get_group_participants(group_id: int, db: Session = Depends(get_db)):
    return db.query(GroupParticipant).filter(GroupParticipant.group_id == group_id).all()

@router.delete("/{participant_id}")
def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    participant = db.get(GroupParticipant, participant_id)

    if not participant:
        raise HTTPException(404, "Participant not found")

    db.delete(participant)
    db.commit()

    return {
        "message": "Participant deleted"
    }