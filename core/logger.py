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
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # 3. Добавляем вывод в файл с ротацией, архивацией и JSON (если включено)
    logger.add(
        settings.LOG_PATH,
        rotation=settings.LOG_ROTATION,     # 5 MB
        retention=settings.LOG_RETENTION,   # 15 days
        compression=settings.LOG_COMPRESSION, # zip
        level=settings.LOG_LEVEL,
        serialize=settings.LOG_SERIALIZE,   # JSON or Text
        encoding="utf-8",
        # enqueue=True - Важно! Делает запись асинхронной и потокобезопасной
        enqueue=True 
    )

    return logger

# Инициализируем логгер сразу при импорте
logger = setup_logger()