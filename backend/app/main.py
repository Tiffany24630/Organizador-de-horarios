from fastapi import FastAPI
from app.database.base import Base
from app.database.connection import engine
from app.models.person import Person
from app.models.activity import Activity
from app.models.space import Space
from app.api.routes.person_routes import router as person_router
from app.api.routes.activity_routes import router as activity_router
from app.api.routes.space_routes import router as space_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Organizador de horariso API",
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

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

app.include_router(person_router)
app.include_router(activity_router)
app.include_router(space_router)