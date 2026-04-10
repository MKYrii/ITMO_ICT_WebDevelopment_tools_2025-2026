from sqlmodel import SQLModel, Session, create_engine

from app.core.config import DB_URL

_engine_kwargs: dict = {"echo": True}
if DB_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DB_URL, **_engine_kwargs)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
