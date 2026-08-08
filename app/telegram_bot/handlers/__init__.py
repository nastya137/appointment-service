from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.telegram_bot.api_client import ApiClient


router = Router()

api_client = ApiClient()


@router.message(CommandStart())
async def start_handler(message: Message):
    telegram_user = message.from_user

    user = await api_client.get_or_create_user(
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )

    services = await api_client.get_services()

    builder = InlineKeyboardBuilder()

    for service in services:
        builder.add(
            InlineKeyboardButton(
                text=(
                    f"{service['name']} "
                    f"({service['duration_minutes']} мин.)"
                ),
                callback_data=f"service:{service['id']}",
            )
        )

    builder.adjust(1)

    await message.answer(
        text=(
            f"Здравствуйте, {telegram_user.first_name}!\n\n"
            "Выберите услугу:"
        ),
        reply_markup=builder.as_markup(),
    )