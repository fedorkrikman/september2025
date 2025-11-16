import aiosqlite
from pathlib import Path
from app.config import DATABASE_URL

# Извлекаем путь к БД и делаем его абсолютным
_db_path = DATABASE_URL.replace("sqlite:///", "")
if _db_path.startswith("./"):
    project_root = Path(__file__).parent.parent.parent
    DB_NAME = str(project_root / _db_path[2:])
else:
    DB_NAME = _db_path


async def update_quiz_index(user_id: int, index: int):
    """Обновляет индекс текущего вопроса для пользователя"""
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


async def get_quiz_index(user_id: int) -> int:
    """Получает индекс текущего вопроса для пользователя"""
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

