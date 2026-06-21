from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.proposal_generator_service import (generate_proposals)

router = APIRouter(prefix = "/proposals", tags = ["Proposals"])

@router.post("/generate/{group_id}")
def generate(group_id: int, db: Session = Depends(get_db)):
    return generate_proposals(group_id, db)