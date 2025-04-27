import logging
from pathlib import Path
from aiogram import Router, types, F
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from content.modules import get_module, get_submodule, get_total_modules
from content.texts import get_content
from data.database import update_user_progress

router = Router()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "images"

async def send_module_selection(message: types.Message):
    """Отправляет список модулей для выбора"""
    try:
        builder = InlineKeyboardBuilder()
        for module_id in range(1, get_total_modules() + 1):
            module = get_module(module_id)
            builder.add(types.InlineKeyboardButton(
                text=module['title'],
                callback_data=f"mod_{module_id}"
            ))
        builder.adjust(1)
        await message.answer(
            "📚 Выберите модуль для изучения:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Error sending module selection: {e}")
        await message.answer("⚠️ Ошибка загрузки модулей")

async def send_submodule_selection(callback: types.CallbackQuery, module_id: int):
    """Отправляет список подмодулей выбранного модуля с вертикальным расположением"""
    try:
        module = get_module(module_id)
        if not module:
            await callback.answer("Модуль не найден")
            return

        builder = InlineKeyboardBuilder()
        
        # Вертикальное расположение кнопок подразделов
        for sub_id, submodule in module['submodules'].items():
            builder.row(types.InlineKeyboardButton(
                text=submodule['title'],
                callback_data=f"sub_{module_id}_{sub_id}_1"
            ))
        
        # Кнопка "Назад" в отдельном ряду
        builder.row(types.InlineKeyboardButton(
            text="◀️ Назад к модулям",
            callback_data="back_to_modules"
        ))
        
        await callback.message.edit_text(
            f"📖 Модуль: {module['title']}\n\nВыберите раздел:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Error sending submodule selection: {e}")
        await callback.answer("⚠️ Ошибка загрузки разделов")

async def send_content_page(
    callback: types.CallbackQuery,
    module_id: int,
    submodule_id: int,
    page: int
):
    """Отправляет содержимое страницы"""
    try:
        content = get_content(module_id, submodule_id, page)
        if not content or not content.get('text'):
            await callback.answer("⛔ Материал не найден")
            return

        submodule = get_submodule(module_id, submodule_id)
        total_pages = submodule.get('pages', 1)

        # Навигационные кнопки
        builder = InlineKeyboardBuilder()
        if page > 1:
            builder.add(types.InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"sub_{module_id}_{submodule_id}_{page-1}"
            ))
        if page < total_pages:
            builder.add(types.InlineKeyboardButton(
                text="Далее ➡️",
                callback_data=f"sub_{module_id}_{submodule_id}_{page+1}"
            ))
        builder.row(types.InlineKeyboardButton(
            text="📋 К списку тем",
            callback_data=f"mod_{module_id}"
        ))
        builder.adjust(2)

        # Отправка контента
        if content.get('image'):
            image_path = IMAGES_DIR / content['image']
            try:
                await callback.message.answer_photo(
                    photo=FSInputFile(image_path),
                    caption=content['text'],
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"Image send failed: {e}")
                await callback.message.answer(
                    text=content['text'],
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
        else:
            await callback.message.answer(
                text=content['text'],
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )

        await callback.message.delete()
        await update_user_progress(
            user_id=callback.from_user.id,
            module=module_id,
            submodule=submodule_id,
            page=page
        )

    except Exception as e:
        logger.error(f"Error sending content: {e}")
        await callback.answer("⚠️ Ошибка загрузки материала")

@router.callback_query(F.data.startswith("mod_"))
async def module_handler(callback: types.CallbackQuery):
    try:
        module_id = int(callback.data.split("_")[1])
        await send_submodule_selection(callback, module_id)
    except Exception as e:
        logger.error(f"Module handler error: {e}")
        await callback.answer("⚠️ Ошибка обработки модуля")

@router.callback_query(F.data.startswith("sub_"))
async def submodule_handler(callback: types.CallbackQuery):
    try:
        _, mod, sub, page = callback.data.split("_")
        await send_content_page(callback, int(mod), int(sub), int(page))
    except Exception as e:
        logger.error(f"Submodule handler error: {e}")
        await callback.answer("⚠️ Ошибка обработки раздела")

@router.callback_query(F.data == "back_to_modules")
async def back_handler(callback: types.CallbackQuery):
    try:
        await send_module_selection(callback.message)
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Back handler error: {e}")
        await callback.answer("⚠️ Ошибка возврата")