from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.person import Person
from app.schemas.person import (PersonCreate, PersonUpdate, PersonResponse)

router = APIRouter(prefix="/people", tags=["People"])

@router.get("/", response_model=list[PersonResponse])
def get_people(db: Session = Depends(get_db)):
    return db.query(Person).all()

@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)

    if not person:
        raise HTTPException(
            status_code = 404,
            detail = "Person not found"
        )

    return person

@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(
    person: PersonCreate,
    db: Session = Depends(get_db)
):
    exists = db.query(Person).filter(Person.email == person.email).first()

    if exists:
        raise HTTPException(
            status_code = 400,
            detail = "Person with this email already exists"
        )

    new_person = Person(name=person.name, email=person.email)

    db.add(new_person)
    db.commit()
    db.refresh(new_person)

    return new_person

@router.put("/{person_id}", response_model=PersonResponse)
def update_person(person_id: int, person_data: PersonUpdate, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)

    if not person:
        raise HTTPException(
            status_code = 404,
            detail = "Person not found"
        )

    person.name = person_data.name
    person.email = person_data.email
    person.active = person_data.active

    db.commit()
    db.refresh(person)

    return person

@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)

    if not person:
        raise HTTPException(
            status_code = 404,
            detail = "Person not found"
        )

    db.delete(person)
    db.commit()

    return {"detail": "Person deleted successfully"}