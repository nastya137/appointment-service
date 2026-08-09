from fastapi import APIRouter, Depends

from app.api.dependencies import get_service_service
from app.api.schemas.service import ServiceResponse
from app.services.service_service import ServiceService


router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.get(
    "",
    response_model=list[ServiceResponse],
)
async def get_active_services(
    service: ServiceService = Depends(get_service_service),
):
    return await service.get_active_services()

@router.get(
    "/specialist/{specialist_id}",
    response_model=list[ServiceResponse],
)
async def get_services_by_specialist(
    specialist_id: int,
    service: ServiceService = Depends(get_service_service),
):
    return await service.get_by_specialist(specialist_id)