from fastapi import Depends
from sqlalchemy import orm

from configs.database import get_db


class BaseRepository:
    def __init__(self, session: orm.Session = Depends(get_db)):
        self.__session = session

    @property
    def session(self) -> orm.Session:
        return self.__session
