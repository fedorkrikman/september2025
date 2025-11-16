"""Логика квиза и данные вопросов"""

# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    # Добавьте другие вопросы
]


async def new_quiz(message, question_index: int = 0):
    """Запускает новый квиз или продолжает существующий"""
    from app.db.quiz import update_quiz_index
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram import types
    
    if question_index >= len(quiz_data):
        await message.answer("Квиз завершен! Спасибо за участие!")
        await update_quiz_index(message.from_user.id, 0)
        return
    
    question = quiz_data[question_index]
    
    # Создаем инлайн-клавиатуру с вариантами ответов
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(question['options']):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"quiz_answer_{question_index}_{i}"
        ))
    builder.adjust(1)  # По одной кнопке в ряд
    
    await message.answer(
        f"Вопрос {question_index + 1}/{len(quiz_data)}:\n{question['question']}",
        reply_markup=builder.as_markup()
    )
    
    await update_quiz_index(message.from_user.id, question_index)

