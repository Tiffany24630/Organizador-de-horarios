from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.availability_matrix_service import build_matrix
from app.services.availability_service import build_group_availability
from app.models.activity_group import ActivityGroup
from app.core.project_access import ProjectAccess, require_project_access

router = APIRouter(prefix="/availability", tags=["Availability"])

@router.get("/matrix/{group_id}")
def availability_matrix(group_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    if not db.query(ActivityGroup).filter(ActivityGroup.id_group == group_id, ActivityGroup.project_id == context.project_id).first():
        raise HTTPException(status_code=404, detail="Group not found")
    return build_matrix(group_id, db)

@router.get("/{group_id}")
def get_availability(group_id: int, context: ProjectAccess = Depends(require_project_access), db: Session = Depends(get_db)):
    if not db.query(ActivityGroup).filter(ActivityGroup.id_group == group_id, ActivityGroup.project_id == context.project_id).first():
        raise HTTPException(status_code=404, detail="Group not found")
    return build_group_availability(group_id, db)
