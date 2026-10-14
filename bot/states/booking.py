from aiogram.fsm.state import State, StatesGroup


class BookingState(StatesGroup):
    choosing_service = State()
