from sqlalchemy.orm import Session
from app.services.availability_matrix_service import build_matrix

def get_availability_matrix(group_id: int, db: Session):
    return build_matrix(group_id, db)