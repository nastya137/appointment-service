from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    duration_minutes: int
    price: int | None
    currency: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)