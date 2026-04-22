import functools
import threading
import time
from typing import Any, Optional, Callable


def scheduled_trigger(
    second: Optional[int] = None,
    minute: Optional[int] = None,
    hour: Optional[int] = None,
    day: Optional[int] = None,
    month: Optional[int] = None,
    day_of_week: Optional[int] = None,
    task_impl: Optional[Any] = None
):
    """
    定时触发注解，支持精确到秒的时间配置

    Args:
        second: 秒（0-59），None 表示不限制
        minute: 分（0-59），None 表示不限制
        hour: 时（0-23），None 表示不限制
        day: 日（1-31），None 表示不限制
        month: 月（1-12），None 表示不限制
        day_of_week: 周几（0-6，0=周一），None 表示不限制
        task_impl: 任务实现类实例

    用法:
        @scheduled_trigger(second=0, minute=0, hour=0, task_impl=PddTaskImpl())
        def daily_job(task_impl):
            task_impl.execute(...)

        @scheduled_trigger(second=0, minute=30, task_impl=PddTaskImpl())
        def hourly_job(task_impl):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(
                target=_run_scheduler,
                args=(func, second, minute, hour, day, month, day_of_week, task_impl),
                daemon=True
            )
            thread.start()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _run_scheduler(func, second, minute, hour, day, month, day_of_week, task_impl):
    """定时执行逻辑"""
    while True:
        now = time.localtime()

        if _should_trigger(now, second, minute, hour, day, month, day_of_week):
            try:
                func(task_impl)
            except Exception as e:
                print(f"定时任务执行异常: {e}")

        time.sleep(1)


def _should_trigger(now, second, minute, hour, day, month, day_of_week) -> bool:
    """判断是否应该触发"""
    if second is not None and now.tm_sec != second:
        return False
    if minute is not None and now.tm_min != minute:
        return False
    if hour is not None and now.tm_hour != hour:
        return False
    if day is not None and now.tm_mday != day:
        return False
    if month is not None and now.tm_mon != month:
        return False
    if day_of_week is not None and now.tm_wday != day_of_week:
        return False
    return True