from pydantic import BaseModel


class SpecialistResponse(BaseModel):
    id: int
    display_name: str
    description: str | None

    model_config = {
        "from_attributes": True,
    }