from typing import Optional

from auth_lib import models
from repositories.base import BaseRepository
from auth_lib.schemas import user_schemas
from utils import utils


class UserRepository(BaseRepository):
    """
    Repository class for handling database operations related to User.
    """

    def get_user(self, email: str) -> Optional[models.User]:
        """
        Retrieve a user from the database by email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            models.User: The user object if found.
        """
        return (
            self.session.query(models.User)
            .filter(models.User.email == email)
            .one_or_none()
        )

    def create_user(
        self, new_user_info: user_schemas.UserCreate
    ) -> Optional[models.User]:
        """
        Create a new user in the database.

        Args:
            new_user_info (user_schemas.UserCreate): The user information provided during registration.

        Returns:
            models.User: The newly created user.
        """
        existing_user = (
            self.session.query(models.User)
            .filter(models.User.email == new_user_info.email)
            .one_or_none()
        )

        if existing_user:
            return None

        hashed_password = utils.hash(new_user_info.password)
        new_user_info.password = hashed_password

        new_user = models.User(**new_user_info.model_dump())
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        return new_user
