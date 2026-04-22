# config.py
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional


class Settings:
    """应用配置类"""

    def __init__(self):
        # 加载 .env 文件
        load_dotenv()

        # 应用配置
        self.APP_NAME = os.getenv('APP_NAME', 'Task-Scheduler-Center')
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

        # MySQL 配置
        self.DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
        self.DB_PORT = int(os.getenv('DB_PORT', 3306))
        self.DB_USER = os.getenv('DB_USER', 'root')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
        self.DB_NAME = os.getenv('DB_NAME', 'task_center')

        # Redis 配置
        self.REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
        self.REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        self.REDIS_DB = int(os.getenv('REDIS_DB', 0))
        self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

        # 日志配置
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_PATH = os.getenv('LOG_PATH', 'logs/scheduler.log')

    @property
    def DATABASE_URL(self) -> str:
        """数据库连接URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def REDIS_URL(self) -> Optional[str]:
        """Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_db_config(self) -> dict:
        """获取数据库配置字典"""
        return {
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'database': self.DB_NAME,
            'charset': 'utf8mb4'
        }

    def display_config(self) -> None:
        """打印配置信息（调试用）"""
        print("=" * 50)
        print("应用配置:")
        print(f"  APP_NAME: {self.APP_NAME}")
        print(f"  DEBUG: {self.DEBUG}")
        print(f"  LOG_LEVEL: {self.LOG_LEVEL}")
        print("\n数据库配置:")
        print(f"  DB_HOST: {self.DB_HOST}")
        print(f"  DB_PORT: {self.DB_PORT}")
        print(f"  DB_USER: {self.DB_USER}")
        print(f"  DB_PASSWORD: {'*' * len(self.DB_PASSWORD) if self.DB_PASSWORD else 'None'}")
        print(f"  DB_NAME: {self.DB_NAME}")
        print(f"  DATABASE_URL: {self.DATABASE_URL}")
        print("\nRedis配置:")
        print(f"  REDIS_HOST: {self.REDIS_HOST}")
        print(f"  REDIS_PORT: {self.REDIS_PORT}")
        print(f"  REDIS_DB: {self.REDIS_DB}")
        print(f"  REDIS_PASSWORD: {'*' * len(self.REDIS_PASSWORD) if self.REDIS_PASSWORD else 'None'}")
        print("=" * 50)


# 创建全局配置实例
settings = Settings()