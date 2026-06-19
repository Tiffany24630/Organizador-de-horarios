from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.person import Person
from app.schemas.person import PersonCreate
from app.schemas.person import PersonResponse

router = APIRouter(prefix="/people", tags=["People"])

@router.get("/", response_model=list[PersonResponse])
def get_people(db: Session = Depends(get_db)):
    return db.query(Person).all()

@router.post("/", response_model=PersonResponse)
def create_person(
    person: PersonCreate,
    db: Session = Depends(get_db)
):
    new_person = Person(name=person.name, email=person.email)

    db.add(new_person)
    db.commit()
    db.refresh(new_person)

    return new_person