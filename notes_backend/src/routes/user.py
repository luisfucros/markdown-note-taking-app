from fastapi import APIRouter, Depends, status
from schemas import token_schemas, user_schemas
from services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=token_schemas.Token
)
def register_user(user: user_schemas.UserCreate, user_service: UserService = Depends()):
    print(user.model_dump())
    response = user_service.create_user(user)
    return response


@router.get("/{email}", response_model=user_schemas.UserOut)
def get_user(email: str, user_service: UserService = Depends()):
    user = user_service.get_user(email)
    return user
