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
from app.api.routes.person_routes import router as person_router
from app.api.routes.activity_routes import router as activity_router
from app.api.routes.space_routes import router as space_router
from app.api.routes.time_block_routes import (router as time_block_router)
from app.api.routes.availability_routes import (router as availability_router)
from app.api.routes.proposal_routes import (router as proposal_router)
from app.models.proposal_attendance import ProposalAttendance
from app.models.accepted_schedule import AcceptedSchedule
from app.models.proposal_history import ProposalHistory
from app.models.proposed_schedule import ProposedSchedule
from app.models.proposed_session import ProposedSession

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

app.include_router(person_router)
app.include_router(activity_router)
app.include_router(space_router)
app.include_router(time_block_router)
app.include_router(availability_router)
app.include_router(proposal_router)
app.include_router(group_router)