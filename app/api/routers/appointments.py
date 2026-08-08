from datetime import date

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_appointment_service
from app.api.schemas.appointment import AppointmentResponse, AppointmentCreate, AvailableSlotResponse
from app.services.appointment_service import AppointmentService


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.get(
    "/available-slots",
    response_model=list[AvailableSlotResponse],
)
async def get_available_slots(
    specialist_id: int,
    service_id: int,
    target_date: date,
    service: AppointmentService = Depends(get_appointment_service),
):
    slots = await service.get_available_slots(
        specialist_id=specialist_id,
        service_id=service_id,
        target_date=target_date,
    )

    return [
        AvailableSlotResponse(
            start_datetime=start,
            end_datetime=end,
        )
        for start, end in slots
    ]

@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
async def get_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.get_by_id(appointment_id)

@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    data: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.create(
        user_id=data.user_id,
        specialist_id=data.specialist_id,
        service_id=data.service_id,
        start_datetime=data.start_datetime,
        contact_type=data.contact_type,
        contact_value=data.contact_value,
        problem_description=data.problem_description,
    )