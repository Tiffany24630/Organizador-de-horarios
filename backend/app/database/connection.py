import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = os.environ.get("DATABASE_URL", "").strip()

if database_url:
    # Neon supplies a PostgreSQL URL. Accept the legacy postgres:// prefix too.
    if database_url.startswith("postgres://"):
        DATABASE_URL = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        DATABASE_URL = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        DATABASE_URL = database_url
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # Keep SQLite as the local-development fallback and for the desktop app.
    default_database = Path(__file__).resolve().parents[2] / "scheduler.db"
    database_path = Path(os.environ.get("SCHEDULER_DB_PATH", default_database)).resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{database_path.as_posix()}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
