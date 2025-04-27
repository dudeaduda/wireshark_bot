import logging
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from content.modules import get_module, get_submodule
from data.database import get_user_progress, update_user_progress
from content.questions import QUESTIONS

router = Router()
logger = logging.getLogger(__name__)

async def show_test_selection(message: types.Message):
    """Показывает список доступных тестов"""
    try:
        builder = InlineKeyboardBuilder()
        completed = (await get_user_progress(message.from_user.id))['completed_modules']
        
        for module_id in range(1, 6):  # Для всех 5 модулей
            module = get_module(module_id)
            if not module:
                continue
                
            status = "✅" if module_id in completed else "🔒"
            builder.add(types.InlineKeyboardButton(
                text=f"{status} {module['title']}",
                callback_data=f"test_select_{module_id}"
            ))
        
        builder.adjust(1)
        await message.answer(
            "📝 Выберите тест для прохождения:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Test selection error: {e}")
        await message.answer("⚠️ Ошибка загрузки тестов")

async def start_test(callback: types.CallbackQuery, module_id: int):
    """Начинает тест по выбранному модулю"""
    try:
        module = get_module(module_id)
        if not module:
            await callback.answer("Модуль не найден")
            return

        questions = QUESTIONS.get(module_id, [])
        if not questions:
            await callback.answer("Тест для этого модуля пока недоступен")
            return

        await callback.message.edit_text(
            f"🧠 Тест: {module['title']}\n\n"
            f"Количество вопросов: {len(questions)}\n"
            "Нажмите 'Начать', чтобы приступить к тестированию.",
            reply_markup=InlineKeyboardBuilder().add(
                types.InlineKeyboardButton(
                    text="Начать тест",
                    callback_data=f"test_start_{module_id}_0_0"  # module_id, q_index, score
                )
            ).as_markup()
        )
    except Exception as e:
        logger.error(f"Test start error: {e}")
        await callback.answer("⚠️ Ошибка запуска теста")

async def show_question(callback: types.CallbackQuery, module_id: int, q_index: int, score: int):
    """Показывает вопрос теста"""
    try:
        questions = QUESTIONS.get(module_id, [])
        if q_index >= len(questions):
            await finish_test(callback, module_id, score)
            return

        question = questions[q_index]
        builder = InlineKeyboardBuilder()

        for i, option in enumerate(question['options']):
            builder.add(types.InlineKeyboardButton(
                text=option,
                callback_data=f"test_answer_{module_id}_{q_index}_{score}_{i}"
            ))
        
        builder.adjust(1)
        await callback.message.edit_text(
            f"❓ Вопрос {q_index + 1}/{len(questions)}\n\n{question['text']}",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Question show error: {e}")
        await callback.answer("⚠️ Ошибка загрузки вопроса")

async def handle_answer(callback: types.CallbackQuery, module_id: int, q_index: int, score: int, answer_idx: int):
    """Обрабатывает ответ пользователя"""
    try:
        questions = QUESTIONS.get(module_id, [])
        question = questions[q_index]
        
        if answer_idx == question['correct']:
            score += 1
            await callback.answer("✅ Верно!")
        else:
            await callback.answer("❌ Неверно! Правильный ответ: " + question['options'][question['correct']])
        
        await show_question(callback, module_id, q_index + 1, score)
    except Exception as e:
        logger.error(f"Answer handling error: {e}")
        await callback.answer("⚠️ Ошибка обработки ответа")

async def finish_test(callback: types.CallbackQuery, module_id: int, score: int):
    """Завершает тест и показывает результаты с исправленной логикой"""
    try:
        questions = QUESTIONS.get(module_id, [])
        total = len(questions)
        percentage = int((score / total) * 100) if total > 0 else 0
        
        if percentage >= 70:
            result = (
                "✅ <b>Тест пройден успешно!</b>\n\n"
                f"Вы правильно ответили на {score} из {total} вопросов.\n"
                f"Процент правильных ответов: {percentage}%\n\n"
                "Модуль добавлен в список завершенных."
            )
            
            # Обновляем прогресс
            await update_user_progress(
                user_id=callback.from_user.id,
                module=module_id,
                mark_completed=True
            )
        else:
            result = (
                "❌ <b>Тест не пройден</b>\n\n"
                f"Вы правильно ответили на {score} из {total} вопросов.\n"
                f"Процент правильных ответов: {percentage}%\n\n"
                "Для успешного прохождения необходимо набрать 70% и более.\n"
                "Попробуйте изучить материал еще раз."
            )
        
        # Создаем клавиатуру с кнопками
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text="Вернуться к тестам",
                callback_data="back_to_tests"
            )
        )
        
        if percentage < 70:
            builder.row(
                types.InlineKeyboardButton(
                    text="Попробовать снова",
                    callback_data=f"test_start_{module_id}_0_0"
                )
            )
        
        await callback.message.edit_text(
            result,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Test finish error: {e}", exc_info=True)
        await callback.answer("⚠️ Произошла ошибка при сохранении результатов")

# Обработчики
@router.callback_query(F.data.startswith("test_select_"))
async def test_select_handler(callback: types.CallbackQuery):
    module_id = int(callback.data.split("_")[2])
    await start_test(callback, module_id)

@router.callback_query(F.data.startswith("test_start_"))
async def test_start_handler(callback: types.CallbackQuery):
    _, _, module_id, q_index, score = callback.data.split("_")
    await show_question(callback, int(module_id), int(q_index), int(score))

@router.callback_query(F.data.startswith("test_answer_"))
async def test_answer_handler(callback: types.CallbackQuery):
    _, _, module_id, q_index, score, answer_idx = callback.data.split("_")
    await handle_answer(callback, int(module_id), int(q_index), int(score), int(answer_idx))

@router.callback_query(F.data == "back_to_tests")
async def back_to_tests_handler(callback: types.CallbackQuery):
    await show_test_selection(callback.message)