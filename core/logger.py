import sys
from loguru import logger
from core.config import settings

def setup_logger():
    # 1. Удаляем стандартный обработчик (чтобы не дублировать логи в консоль, если нужно, или перенастроить)
    logger.remove()

    # 2. Добавляем вывод в консоль (цветной, красивый)
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        backtrace=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # 3. Добавляем вывод в файл с ротацией, архивацией и JSON (если включено)
    logger.add(
        settings.LOG_PATH,
        level=settings.LOG_LEVEL,               # Например, DEBUG или INFO
        rotation=settings.LOG_ROTATION,         # 5 MB
        retention=settings.LOG_RETENTION,       # 15 days
        compression=settings.LOG_COMPRESSION,   # zip
        serialize=settings.LOG_SERIALIZE,       # JSON or Text
        encoding="utf-8",
        enqueue=True,                           # enqueue=True - Важно! Делает запись асинхронной и потокобезопасной
        backtrace=False                         # Сохранять подробный трейс ошибки
    )

    # 4. ФАЙЛ ОШИБОК (Только ERROR и CRITICAL)
    logger.add(
        settings.LOG_PATH_ERRORS,
        level="ERROR",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression=settings.LOG_COMPRESSION,
        serialize=settings.LOG_SERIALIZE_ERRORS,
        encoding="utf-8",
        enqueue=True,
        backtrace=False,                         # Сохранять подробный трейс ошибки
        diagnose=True,                           # Сохранять значения переменных при ошибке
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

    return logger

# Инициализируем логгер сразу при импорте
logger = setup_logger()