import os
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

class Settings:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_PATH = os.getenv("LOG_PATH", "logs/app.log")
    LOG_ROTATION = os.getenv("LOG_ROTATION", "5 MB")
    LOG_RETENTION = os.getenv("LOG_RETENTION", "15 days")
    LOG_COMPRESSION = os.getenv("LOG_COMPRESSION", "zip")
    # Преобразуем строку "True" в булево значение
    LOG_SERIALIZE = os.getenv("LOG_SERIALIZE", "False").lower() == "true"

settings = Settings()