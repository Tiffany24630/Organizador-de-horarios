import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

default_database = Path(__file__).resolve().parents[2] / "scheduler.db"
DATABASE_PATH = Path(os.environ.get("SCHEDULER_DB_PATH", default_database)).resolve()
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
