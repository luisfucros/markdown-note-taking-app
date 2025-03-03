import models
from authentication import oauth2
from fastapi import Depends, HTTPException, status
from repositories.user import UserRepository
from schemas import token_schemas, user_schemas


class UserService:
    """
    Service class for handling user-related business logic.
    """

    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repo = user_repository

    def get_user(self, email: str) -> models.User:
        """
        Fetch a user by email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            models.User: The user object if found.
        """
        user = self.user_repo.get_user(email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found",
            )
        return user

    def create_user(
        self, new_user_info: user_schemas.UserCreate
    ) -> token_schemas.Token:
        """
        Create a new user and return an authentication token.

        Args:
            new_user_info (user_schemas.UserCreate): The user data to create.

        Returns:
            token_schemas.Token: The access token for the new user.
        """
        new_user = self.user_repo.create_user(new_user_info=new_user_info)

        access_token = oauth2.create_access_token(data={"user_email": new_user.email})

        return token_schemas.Token(access_token=access_token, token_type="bearer")
