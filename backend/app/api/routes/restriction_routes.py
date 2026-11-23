from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.restriction import Restriction
from app.models.activity_group import ActivityGroup
from app.schemas.restriction import RestrictionCreate, RestrictionResponse
from app.core.project_access import ProjectAccess, require_project_access

router = APIRouter(prefix="/restrictions", tags=["Restrictions"])

@router.post("/", response_model=RestrictionResponse)
def create_restriction(data: RestrictionCreate, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    if not db.query(ActivityGroup).filter(ActivityGroup.id_group == data.group_id, ActivityGroup.project_id == context.project_id).first():
        raise HTTPException(status_code=404, detail="Group not found")
    restriction = Restriction(**data.model_dump())

    db.add(restriction)
    db.commit()
    db.refresh(restriction)

    return restriction

@router.get("/", response_model=list[RestrictionResponse])
def get_restrictions(context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    return db.query(Restriction).join(ActivityGroup).filter(ActivityGroup.project_id == context.project_id).all()

@router.get("/{restriction_id}", response_model=RestrictionResponse)
def get_restriction(restriction_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    restriction = db.query(Restriction).join(ActivityGroup).filter(Restriction.id_restriction == restriction_id, ActivityGroup.project_id == context.project_id).first()

    if not restriction:
        raise HTTPException(status_code=404, detail="Restriction not found")

    return restriction

@router.delete("/{restriction_id}")
def delete_restriction(restriction_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    restriction = db.query(Restriction).join(ActivityGroup).filter(Restriction.id_restriction == restriction_id, ActivityGroup.project_id == context.project_id).first()

    if not restriction:
        raise HTTPException(status_code=404, detail="Restriction not found")

    db.delete(restriction)
    db.commit()

    return {
        "message": "Restriction deleted"
    }
