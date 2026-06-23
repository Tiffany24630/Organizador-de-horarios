from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.base import Base
from app.database.connection import engine
from app.models.person import Person
from app.models.activity import Activity
from app.models.space import Space
from app.models.time_block import TimeBlock
from app.models.activity_group import ActivityGroup
from app.models.group_participant import GroupParticipant
from app.models.restriction import Restriction
from app.models.space_reservation import SpaceReservation
from app.models.proposal_attendance import ProposalAttendance
from app.models.accepted_schedule import AcceptedSchedule
from app.models.proposal_history import ProposalHistory
from app.models.proposed_schedule import ProposedSchedule
from app.models.proposed_session import ProposedSession
from app.api.routes.statistics_routes import router as statistics_router
from app.api.routes.person_routes import router as person_router
from app.api.routes.activity_routes import router as activity_router
from app.api.routes.space_routes import router as space_router
from app.api.routes.time_block_routes import router as time_block_router
from app.api.routes.availability_routes import router as availability_router
from app.api.routes.proposal_routes import router as proposal_router
from app.api.routes.group_routes import router as group_router
from app.api.routes.group_participant_routes import router as group_participant_router
from app.api.routes.restriction_routes import router as restriction_router
from app.api.routes.import_routes import router as import_router
from app.api.routes.space_reservation_routes import router as space_reservation_router
from app.api.routes.proposal_attendance_routes import router as proposal_attendance_router
from app.api.routes.proposed_session_routes import router as proposed_session_router
from app.api.routes.accepted_schedule_routes import router as accepted_schedule_router
from app.api.routes.proposal_history_routes import router as proposal_history_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Organizador de horarios API",
    description="""
API para la gestión inteligente de horarios colaborativos.

Características:

- Gestión de personas
- Gestión de actividades
- Gestión de espacios
- Importación de horarios
- Optimización de actividades grupales
- Generación de propuestas automáticas

Desarrollado con FastAPI.
"""
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.get("/")
def root():
    return {
        "application": "Organizador de Horarios",
        "version": "1.0.0",
        "docs": "/docs"
    }

app.include_router(person_router)
app.include_router(activity_router)
app.include_router(space_router)
app.include_router(time_block_router)
app.include_router(availability_router)
app.include_router(proposal_router)
app.include_router(group_router)
app.include_router(group_participant_router)
app.include_router(restriction_router)
app.include_router(space_reservation_router)
app.include_router(import_router)
app.include_router(proposal_attendance_router)
app.include_router(proposed_session_router)
app.include_router(accepted_schedule_router)
app.include_router(proposal_history_router)
app.include_router(statistics_router)