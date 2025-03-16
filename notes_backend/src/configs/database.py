from typing import Generator

from configs.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://%s:%s@%s:%s/%s" % (
    settings.database_username,
    settings.database_password,
    settings.database_hostname,
    settings.database_port,
    settings.database_name,
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
