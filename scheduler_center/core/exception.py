from fastapi import Request
from .response import unified_send
from .logger import logger


async def global_exception_handler(request: Request, exc: Exception):
    # 这里可以记录错误日志到数据库
    logger.error(f"Global Error: {str(exc)}")
    return unified_send(500, f"系统异常: {str(exc)}", None)