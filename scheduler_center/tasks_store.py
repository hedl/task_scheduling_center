from services.scheduler_mgr import distributed_task
from services.dispatcher import dispatch_pinduoduo_tasks
from core.logger import logger

@distributed_task("pdd_sync_task")
async def scheduled_pdd_task():
    logger.info("开始执行定时任务：拼多多平台同步")
    await dispatch_pinduoduo_tasks("pinduoduo")