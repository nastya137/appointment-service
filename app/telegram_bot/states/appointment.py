from aiogram.fsm.state import State, StatesGroup


class AppointmentState(StatesGroup):
    selecting_service = State()
    selecting_date = State()
    selecting_time = State()
    confirming = State()