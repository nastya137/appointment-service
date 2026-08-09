from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import specialists
from app.api.exception_handler import appointment_not_found_handler
from app.api.routers import services
from app.api.routers.appointments import router as appointments_router
from app.database.session import create_database
from app.exceptions.appointment import AppointmentNotFoundError
from app.api.routers import users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await create_database()
    yield


app = FastAPI(
    title="Psychologist Booking API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    AppointmentNotFoundError,
    appointment_not_found_handler,
)

app.include_router(appointments_router)
app.include_router(services.router)
app.include_router(users.router)
app.include_router(specialists.router)


