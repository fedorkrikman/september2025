from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def register_start(dp):
    """Регистрирует обработчики команды /start"""
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        # Создаем сборщика клавиатур типа Reply
        builder = ReplyKeyboardBuilder()
        # Добавляем в сборщик одну кнопку
        builder.add(types.KeyboardButton(text="Начать игру"))
        # Прикрепляем кнопки к сообщению
        await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

