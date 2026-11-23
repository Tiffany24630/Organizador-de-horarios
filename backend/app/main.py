import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.base import Base
from app.database.connection import engine, SessionLocal
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
from app.models.user import User, UserSession, PasswordRecoveryRequest
from app.models.project import Project, ProjectMembership, ProjectInvite, GuestSession
from app.core.security import hash_password, normalize_email, validate_password
from app.core.project_access import require_project_access
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.admin_routes import router as admin_router
from app.api.routes.project_routes import router as project_router
from app.core.logger import logger
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
from sqlalchemy import inspect, text

Base.metadata.create_all(bind=engine)

# Project ownership is introduced after the original SQLite schema. Keep the
# migration additive so existing local databases can still be opened safely.
for table in ("persons", "activity_groups", "spaces"):
    if "project_id" not in {column["name"] for column in inspect(engine).get_columns(table)}:
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN project_id INTEGER"))


def bootstrap_superadmin() -> None:
    email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "").strip()
    password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "")
    name = os.environ.get("BOOTSTRAP_ADMIN_NAME", "Superadmin").strip() or "Superadmin"
    if not email or not password:
        return
    try:
        validate_password(password)
    except ValueError:
        return
    db = SessionLocal()
    try:
        email = normalize_email(email)
        if db.query(User).filter(User.system_role == "superadmin").first():
            return
        if db.query(User).filter(User.email == email).first():
            return
        db.add(User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            system_role="superadmin",
            must_change_password=True,
        ))
        db.commit()
    finally:
        db.close()


bootstrap_superadmin()

# create_all does not alter an already existing SQLite table. Keep desktop
# databases created by older versions usable without requiring a destructive
# rebuild or a migration tool.
if "room" not in {column["name"] for column in inspect(engine).get_columns("time_blocks")}:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE time_blocks ADD COLUMN room VARCHAR(100)"))

for table, column, definition in (
    ("proposed_schedules", "attending_count", "INTEGER DEFAULT 0"),
    ("proposed_schedules", "total_people", "INTEGER DEFAULT 0"),
    ("proposed_schedules", "explanation", "TEXT"),
    ("proposal_attendance", "reason", "VARCHAR(250)"),
    ("proposal_attendance", "conflicts_json", "TEXT"),
):
    if column not in {item["name"] for item in inspect(engine).get_columns(table)}:
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))

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
    allow_origins = [origin.strip() for origin in os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,null",
    ).split(",") if origin.strip()],
    allow_methods = ["*"],
    allow_headers = ["*"],
    allow_credentials = True,
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

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"Status: {response.status_code}")

    return response

# All scheduling/data endpoints require an authenticated member or a valid
# project invitation. Authentication and project management routes below are
# intentionally public or protected by their own dependencies.
project_dependency = [Depends(require_project_access)]
app.include_router(person_router, dependencies=project_dependency)
app.include_router(activity_router, dependencies=project_dependency)
app.include_router(space_router, dependencies=project_dependency)
app.include_router(time_block_router, dependencies=project_dependency)
app.include_router(availability_router, dependencies=project_dependency)
app.include_router(proposal_router, dependencies=project_dependency)
app.include_router(group_router, dependencies=project_dependency)
app.include_router(group_participant_router, dependencies=project_dependency)
app.include_router(restriction_router, dependencies=project_dependency)
app.include_router(space_reservation_router, dependencies=project_dependency)
app.include_router(import_router, dependencies=project_dependency)
app.include_router(proposal_attendance_router, dependencies=project_dependency)
app.include_router(proposed_session_router, dependencies=project_dependency)
app.include_router(accepted_schedule_router, dependencies=project_dependency)
app.include_router(proposal_history_router, dependencies=project_dependency)
app.include_router(statistics_router, dependencies=project_dependency)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(project_router)
