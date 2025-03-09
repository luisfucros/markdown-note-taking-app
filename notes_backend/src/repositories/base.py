from fastapi import Depends
from sqlalchemy import orm

from configs.database import get_db


class BaseRepository:
    """Base repository class providing common database session management functionality."""

    def __init__(self, session: orm.Session = Depends(get_db)):
        self.__session = session

    @property
    def session(self) -> orm.Session:
        """Provides access to the database session."""
        return self.__session
