from fastapi import FastAPI
from core.exception import global_exception_handler
from core.response import unified_send
from services.scheduler_mgr import scheduler
from tasks_store import scheduled_pdd_task
from apscheduler.triggers.cron import CronTrigger
import uvicorn
import asyncio

app = FastAPI()

# 注册全局异常捕获
app.add_exception_handler(Exception, global_exception_handler)

@app.on_event("startup")
async def load_tasks():
    # 1. 这里可以从数据库读取任务配置并动态添加
    # 2. 也可以手动添加被注解标记的任务
    scheduler.add_job(
        scheduled_pdd_task,
        CronTrigger.from_crontab("*/5 * * * *"), # 每5分钟一次
        id="pdd_sync_task"
    )
    scheduler.start()

@app.post("/tasks/run_now")
async def trigger_task_manually(platform: str):
    """
    接口请求直接启动服务
    """
    if platform == "pinduoduo":
        # 异步执行，不阻塞接口返回
        asyncio.create_task(scheduled_pdd_task())
        return unified_send(200, "拼多多任务已手动触发", None)
    return unified_send(400, "未知平台", None)

@app.get("/health")
async def health_check():
    return unified_send(200, "OK", {"status": "running"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)