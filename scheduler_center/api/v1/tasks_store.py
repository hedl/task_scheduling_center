from services.scheduler_mgr import distributed_task
from services.dispatcher import dispatch_pinduoduo_tasks
from core.logger import logger, log_to_db
from database.db import SessionLocal
from database.models import TaskConfig  # 假设这是你的配置表


@distributed_task("pdd_sync_job")
async def pdd_dispatch_job():
    """
    注解方式自动定时启动的任务
    """
    logger.info("--- 定时任务开始：拼多多平台任务分发 ---")
    try:
        # 1. 可以在这里查询任务配置表，确认该任务是否开启
        db = SessionLocal()
        config = db.query(TaskConfig).filter(TaskConfig.task_name == "pdd_sync_job").first()

        if config and config.is_active == 0:
            logger.info("任务已在配置表中禁用，跳过执行")
            return

        # 2. 调用核心算法进行分发
        # 这里传递平台标识，内部会查询店铺并分发给子服务
        await dispatch_pinduoduo_tasks(platform="pinduoduo")

        log_to_db("INFO", "拼多多分发任务执行成功", "pdd_sync_job")

    except Exception as e:
        logger.error(f"拼多多定时任务执行失败: {str(e)}")
        log_to_db("ERROR", f"执行异常: {str(e)}", "pdd_sync_job")
    finally:
        db.close()


@distributed_task("other_platform_job")
async def other_job():
    # 其他平台的逻辑...
    pass