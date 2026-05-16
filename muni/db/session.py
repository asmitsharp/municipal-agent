from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from muni.config import get_settings


def get_database_url() -> str:
    return get_settings().database_url


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    sqlite_path = database_url.replace("sqlite:///", "", 1)
    if sqlite_path == ":memory:":
        return
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)


def make_engine(database_url: Optional[str] = None) -> Engine:
    database_url = database_url or get_database_url()
    _ensure_sqlite_parent(database_url)
    return create_engine(database_url, future=True)


def check_database(database_url: Optional[str] = None) -> str:
    engine = make_engine(database_url)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return "connected"


def check_postgis(database_url: Optional[str] = None) -> str:
    database_url = database_url or get_database_url()
    if not database_url.startswith(("postgresql://", "postgresql+")):
        return "skipped: database is not PostgreSQL"
    engine = make_engine(database_url)
    with engine.connect() as connection:
        version = connection.execute(text("SELECT postgis_version()")).scalar_one()
    return f"available: {version}"


from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_sessionmaker = None

def _get_or_create_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = make_engine()
    return _engine

def _get_or_create_sessionmaker() -> sessionmaker:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = sessionmaker(bind=_get_or_create_engine())
    return _sessionmaker

@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = _get_or_create_sessionmaker()()
    try:
        yield session
    finally:
        session.close()
