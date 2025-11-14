import asyncio
from app.bot import make_bot_and_dp
from app.handlers.start import register_start
from app.handlers.quiz import register_quiz
from app.db.core import init_db

async def main():
    await init_db()
    bot, dp = make_bot_and_dp()
    register_start(dp)
    register_quiz(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())