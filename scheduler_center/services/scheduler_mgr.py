from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.config import settings
from redis import Redis
import functools

scheduler = AsyncIOScheduler()
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


def distributed_task(task_id: str):
    """
    自定义注解：实现分布式环境下的任务注册与锁定
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 尝试获取 Redis 锁，有效期设为1分钟，防止重复执行
            lock_key = f"lock:task:{task_id}"
            if redis_conn.set(lock_key, "1", ex=60, nx=True):
                try:
                    return await func(*args, **kwargs)
                finally:
                    # 如果任务执行很快，这里不建议立即删锁，由ex自动过期防止多实例并发
                    pass
            else:
                print(f"Task {task_id} is already running in another instance.")

        # 将函数存入全局变量，方便后续手动调用或动态修改
        func.is_task = True
        return wrapper

    return decorator