import logging
import sys
from logging.handlers import RotatingFileHandler
from .config import settings
import os

# 创建日志目录
if not os.path.exists("logs"):
    os.makedirs("logs")

def setup_logger():
    logger = logging.getLogger(settings.APP_NAME)
    logger.setLevel(settings.LOG_LEVEL)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出
    file_handler = RotatingFileHandler(
        settings.LOG_PATH, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

def log_to_db(level: str, message: str, task_id: str = None):
    """
    你可以调用这个方法，将关键日志同步写入你的已有的日志表
    """
    # 这里编写你已有的数据库写入逻辑
    # from database.db import SessionLocal
    # from database.models import LogModel
    # db = SessionLocal()
    # ...
    logger.info(f"[DB_LOG] {level}: {message}")