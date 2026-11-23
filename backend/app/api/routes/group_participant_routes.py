from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.connection import get_db
from app.models.group_participant import GroupParticipant
from app.models.activity_group import ActivityGroup
from app.models.person import Person
from app.schemas.group_participant import GroupParticipantCreate, GroupParticipantResponse
from app.core.project_access import ProjectAccess, require_project_access

router = APIRouter(prefix="/group-participants", tags=["Group Participants"])

@router.post("/", response_model=GroupParticipantResponse)
def create_participant(data: GroupParticipantCreate, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    if not db.query(ActivityGroup).filter(ActivityGroup.id_group == data.group_id, ActivityGroup.project_id == context.project_id).first():
        raise HTTPException(404, "Group not found")
    if not db.query(Person).filter(Person.id_person == data.person_id, Person.project_id == context.project_id).first():
        raise HTTPException(404, "Person not found")
    participant = GroupParticipant(**data.model_dump())

    exists = db.query(GroupParticipant).filter(GroupParticipant.group_id == data.group_id, GroupParticipant.person_id == data.person_id).first()

    if exists:
        raise HTTPException(400, "Participant already exists in group")

    db.add(participant)
    db.commit()
    db.refresh(participant)

    return participant

@router.get("/",response_model=list[GroupParticipantResponse])
def get_participants(context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    return db.query(GroupParticipant).join(ActivityGroup).filter(ActivityGroup.project_id == context.project_id).all()

@router.get("/{group_id}")
def get_group_participants(group_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    return db.query(GroupParticipant).join(ActivityGroup).filter(GroupParticipant.group_id == group_id, ActivityGroup.project_id == context.project_id).all()

@router.delete("/{participant_id}")
def delete_participant(participant_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    participant = db.query(GroupParticipant).join(ActivityGroup).filter(GroupParticipant.id_participant == participant_id, ActivityGroup.project_id == context.project_id).first()

    if not participant:
        raise HTTPException(404, "Participant not found")

    db.delete(participant)
    db.commit()

    return {
        "message": "Participant deleted"
    }
