from auth_lib.schemas import token_schemas, user_schemas
from fastapi import APIRouter, Depends, HTTPException, status
from services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=token_schemas.Token
)
def register_user(user: user_schemas.UserCreate, user_service: UserService = Depends()):
    response = user_service.create_user(user)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return response


@router.get("/{email}", response_model=user_schemas.UserOut)
def get_user(email: str, user_service: UserService = Depends()):
    user = user_service.get_user(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' not found",
        )
    return user
