from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_user_service
from app.api.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/telegram",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_or_create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.get_or_create_user(
        telegram_id=data.telegram_id,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
    )