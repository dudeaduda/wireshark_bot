from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в бота по обучению Wireshark!")

@router.message(F.text == "📚 Теория")
async def theory_menu(message: types.Message):
    from handlers.theory import send_module_selection
    await send_module_selection(message)

@router.message(F.text == "🔍 Практика")
async def practice_menu(message: types.Message):
    from handlers.practice import show_practice_menu
    await show_practice_menu(message)

@router.message(F.text == "📝 Тесты")
async def tests_menu(message: types.Message):
    from handlers.tests import show_test_selection
    await show_test_selection(message)

@router.message(F.text == "🔗 Ресурсы")
async def resources_menu(message: types.Message):
    await message.answer("Официальные ресурсы:\n1. Wireshark: wireshark.org\n2. Nmap: nmap.org")

