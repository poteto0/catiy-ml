from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.infra.db.engine import engine


def get_db() -> Generator[Session]:
    with sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )() as session:
        yield session
