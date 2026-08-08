from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.appointment import AppointmentNotFoundError


async def appointment_not_found_handler(
    request: Request,
    exc: AppointmentNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Appointment not found"
        },
    )