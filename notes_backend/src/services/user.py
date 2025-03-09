import logging
from typing import Optional

from fastapi import Depends

import models
from authentication import oauth2
from repositories.user import UserRepository
from schemas import token_schemas, user_schemas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for handling user-related business logic.
    """

    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repo = user_repository

    def get_user(self, email: str) -> Optional[models.User]:
        """
        Fetch a user by email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            models.User: The user object if found.
        """
        logger.info(f"Fetching user with email: {email}")
        user = self.user_repo.get_user(email=email)
        if user is None:
            logger.warning(f"User with email {email} not found")
        return user

    def create_user(
        self, new_user_info: user_schemas.UserCreate
    ) -> Optional[token_schemas.Token]:
        """
        Create a new user and return an authentication token.

        Args:
            new_user_info (user_schemas.UserCreate): The user data to create.

        Returns:
            token_schemas.Token: The access token for the new user.
        """
        logger.info(f"Creating new user with email: {new_user_info.email}")
        new_user = self.user_repo.create_user(new_user_info=new_user_info)

        if new_user is None:
            logger.warning(f"User with email: {new_user_info.email} already exists")
            return None

        logger.info(f"User created successfully: {new_user.email}")
        access_token = oauth2.create_access_token(data={"user_email": new_user.email})
        return token_schemas.Token(access_token=access_token, token_type="bearer")
