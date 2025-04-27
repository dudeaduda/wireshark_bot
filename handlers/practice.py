import logging
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from content.modules import get_module
from content.practice_tasks import PRACTICE_TASKS
from data.database import get_user_progress

router = Router()
logger = logging.getLogger(__name__)

async def show_practice_menu(message: types.Message):
    """Показывает меню практических заданий"""
    try:
        progress = await get_user_progress(message.from_user.id)
        builder = InlineKeyboardBuilder()
        
        for module_id in range(1, 6):  # Для всех 5 модулей
            module = get_module(module_id)
            if not module:
                continue
                
            # Проверяем, завершен ли модуль
            if module_id in progress['completed_modules']:
                builder.add(types.InlineKeyboardButton(
                    text=f"✅ {module['title']}",
                    callback_data=f"practice_module_{module_id}"
                ))
            else:
                builder.add(types.InlineKeyboardButton(
                    text=f"🔒 {module['title']}",
                    callback_data="practice_locked"
                ))
        
        builder.adjust(1)
        await message.answer(
            "🔍 Выберите модуль для практических заданий:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Practice menu error: {e}")
        await message.answer("⚠️ Ошибка загрузки заданий")

async def show_module_tasks(callback: types.CallbackQuery, module_id: int):
    """Показывает задания для выбранного модуля"""
    try:
        tasks = PRACTICE_TASKS.get(module_id, [])
        if not tasks:
            await callback.answer("Задания для этого модуля пока недоступны")
            return

        builder = InlineKeyboardBuilder()
        for i, task in enumerate(tasks, 1):
            builder.add(types.InlineKeyboardButton(
                text=f"Задание {i}: {task['title']}",
                callback_data=f"practice_task_{module_id}_{i-1}"
            ))
        
        builder.row(types.InlineKeyboardButton(
            text="◀️ Назад к модулям",
            callback_data="practice_back"
        ))
        builder.adjust(1)
        
        await callback.message.edit_text(
            f"📝 Практические задания для модуля {module_id}:\n\n"
            "Выберите задание для просмотра деталей:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Module tasks error: {e}")
        await callback.answer("⚠️ Ошибка загрузки заданий")

async def show_task_details(callback: types.CallbackQuery, module_id: int, task_index: int):
    """Показывает детали конкретного задания"""
    try:
        tasks = PRACTICE_TASKS.get(module_id, [])
        task = tasks[task_index]
        
        text = (
            f"🔧 <b>{task['title']}</b>\n\n"
            f"<u>Описание задания:</u>\n{task['description']}\n\n"
            f"<u>Критерии проверки:</u>\n{task['check']}\n\n"
            "Выполните задание и отправьте результат (скриншот/файл) с комментарием."
        )
        
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="◀️ Назад к заданиям",
            callback_data=f"practice_module_{module_id}"
        ))
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Task details error: {e}")
        await callback.answer("⚠️ Ошибка загрузки задания")

@router.callback_query(F.data == "practice_locked")
async def handle_locked(callback: types.CallbackQuery):
    await callback.answer("🔒 Сначала завершите теоретический и тестовый модули", show_alert=True)

@router.callback_query(F.data == "practice_back")
async def handle_back(callback: types.CallbackQuery):
    await show_practice_menu(callback.message)

@router.callback_query(F.data.startswith("practice_module_"))
async def handle_module(callback: types.CallbackQuery):
    module_id = int(callback.data.split("_")[2])
    await show_module_tasks(callback, module_id)

@router.callback_query(F.data.startswith("practice_task_"))
async def handle_task(callback: types.CallbackQuery):
    _, _, module_id, task_index = callback.data.split("_")
    await show_task_details(callback, int(module_id), int(task_index))

@router.message(F.document | F.photo)
async def handle_task_submission(message: types.Message):
    """Обрабатывает отправленные файлы/скриншоты"""
    try:
        # можно дальше будет добавить код для проверки заданий
        await message.answer(
            "✅ Ваше задание принято на проверку!\n"
            "Результаты будут отправлены вам в течение 24 часов."
        )
    except Exception as e:
        logger.error(f"Submission error: {e}")
        await message.answer("⚠️ Ошибка при обработке задания")