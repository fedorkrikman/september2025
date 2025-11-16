from aiogram import types, F
from aiogram.filters.command import Command
from app.logic import new_quiz, quiz_data
from app.db.quiz import get_quiz_index, update_quiz_index


def register_quiz(dp):
    """Регистрирует обработчики квиза"""
    
    @dp.message(F.text == "Начать игру")
    @dp.message(Command("quiz"))
    async def cmd_quiz(message: types.Message):
        # Отправляем новое сообщение без кнопок
        await message.answer(f"Давайте начнем квиз!")
        # Запускаем новый квиз
        await new_quiz(message, 0)
    
    @dp.callback_query(F.data.startswith("quiz_answer_"))
    async def process_quiz_answer(callback: types.CallbackQuery):
        """Обрабатывает ответ пользователя на вопрос квиза"""
        # Парсим данные из callback_data: quiz_answer_{question_index}_{answer_index}
        parts = callback.data.split("_")
        question_index = int(parts[2])
        answer_index = int(parts[3])
        
        question = quiz_data[question_index]
        is_correct = answer_index == question['correct_option']
        
        if is_correct:
            await callback.message.answer("✅ Правильно!")
        else:
            correct_answer = question['options'][question['correct_option']]
            await callback.message.answer(f"❌ Неправильно. Правильный ответ: {correct_answer}")
        
        await callback.answer()
        
        # Переходим к следующему вопросу
        next_index = question_index + 1
        await new_quiz(callback.message, next_index)

