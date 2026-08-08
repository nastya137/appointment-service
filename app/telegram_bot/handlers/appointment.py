from datetime import date, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.telegram_bot.api_client import ApiClient

router = Router()
api_client = ApiClient()


@router.callback_query(F.data.startswith("service:"))
async def service_selected(callback: CallbackQuery):
    service_id = int(callback.data.split(":")[1])

    builder = InlineKeyboardBuilder()

    today = date.today()

    for i in range(7):
        target_date = today + timedelta(days=i)

        builder.button(
            text=target_date.strftime("%d.%m"),
            callback_data=(
                f"date:{service_id}:{target_date.isoformat()}"
            ),
        )

    builder.adjust(2)

    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=builder.as_markup(),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("date:"))
async def date_selected(callback: CallbackQuery):
    print("DATE HANDLER CALLED:", callback.data)
    _, service_id, target_date = callback.data.split(":")

    service_id = int(service_id)

    specialist_id = 1

    slots = await api_client.get_available_slots(
        specialist_id=specialist_id,
        service_id=service_id,
        target_date=target_date,
    )

    if not slots:
        await callback.answer(
            "На эту дату свободных слотов нет",
            show_alert=True,
        )
        return

    builder = InlineKeyboardBuilder()

    for slot in slots:
        start_datetime = slot["start_datetime"]

        time_text = start_datetime[11:16]

        builder.button(
            text=time_text,
            callback_data=(
                f"slot:{service_id}:{target_date}:{start_datetime}"
            ),
        )

    builder.adjust(3)

    await callback.message.edit_text(
        "Выберите время:",
        reply_markup=builder.as_markup(),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("slot:"))
async def slot_selected(callback: CallbackQuery):
    _, service_id, target_date, start_datetime = callback.data.split(":", 3)

    service_id = int(service_id)
    specialist_id = 1

    builder = InlineKeyboardBuilder()

    builder.button(
        text="Записаться",
        callback_data=(
            f"confirm:{service_id}:{target_date}:{start_datetime}"
        ),
    )

    builder.button(
        text="Назад",
        callback_data=f"date:{service_id}:{target_date}",
    )

    builder.adjust(1)

    await callback.message.edit_text(
        (
            "Подтвердите запись:\n\n"
            f"Дата: {target_date}\n"
            f"Время: {start_datetime[11:16]}"
        ),
        reply_markup=builder.as_markup(),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_appointment(callback: CallbackQuery):
    _, service_id, target_date, start_datetime = callback.data.split(":", 3)

    service_id = int(service_id)
    specialist_id = 1

    telegram_user = callback.from_user

    contact_type = "telegram"

    if telegram_user.username:
        contact_value = f"@{telegram_user.username}"
    else:
        contact_value = str(telegram_user.id)

    user = await api_client.get_or_create_user(
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )

    appointment = await api_client.create_appointment(
        user_id=user["id"],
        specialist_id=specialist_id,
        service_id=service_id,
        start_datetime=start_datetime,
        contact_type=contact_type,
        contact_value=contact_value,
    )

    await callback.message.edit_text(
        (
            "Запись успешно создана!\n\n"
            f"Дата: {target_date}\n"
            f"Время: {start_datetime[11:16]}"
        )
    )

    await callback.answer()