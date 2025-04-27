from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="📚 Теория"),
        types.KeyboardButton(text="🔍 Практика")
    )
    builder.row(
        types.KeyboardButton(text="📝 Тесты"),
        types.KeyboardButton(text="🔗 Ресурсы")
    )
    return builder.as_markup(resize_keyboard=True)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в бота по обучению Wireshark!",
        reply_markup=get_main_menu()
    )