import os
from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render PostgreSQL connection
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql://", 1
        )
    elif DATABASE_URL.startswith("postgresql://"):
        pass
else:
    # Local development uses SQLite
    DATABASE_PATH = PROJECT_ROOT / "tracewise.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session