from os import getenv
API_TOKEN   = getenv("API_TOKEN", "")
DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./db/quiz_bot.db")
LOG_LEVEL   = getenv("LOG_LEVEL", "INFO")