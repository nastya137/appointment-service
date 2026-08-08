from sqlalchemy import ForeignKey, Table, Column
from app.database.base import Base


specialist_services = Table(
    "specialist_services",
    Base.metadata,

    Column(
        "specialist_id",
        ForeignKey("specialists.id"),
        primary_key=True
    ),

    Column(
        "service_id",
        ForeignKey("services.id"),
        primary_key=True
    )
)