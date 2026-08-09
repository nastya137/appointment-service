from fastapi import APIRouter, Depends

from app.api.dependencies import get_specialist_service
from app.api.schemas.specialist import SpecialistResponse
from app.services.specialist_service import SpecialistService


router = APIRouter(
    prefix="/specialists",
    tags=["Specialists"],
)


@router.get(
    "",
    response_model=list[SpecialistResponse],
)
async def get_active_specialists(
    service: SpecialistService = Depends(get_specialist_service),
):
    return await service.get_active_specialists()