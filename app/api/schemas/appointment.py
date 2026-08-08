from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.appointment_status import AppointmentStatus


class AppointmentCreate(BaseModel):
    user_id: int
    specialist_id: int
    service_id: int
    start_datetime: datetime
    contact_type: str | None = None
    contact_value: str | None = None
    problem_description: str | None = None


class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    specialist_id: int
    service_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: AppointmentStatus
    contact_type: str | None
    contact_value: str | None
    problem_description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AvailableSlotResponse(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
