from fastapi import APIRouter, Body
from database.db import SessionLocal
from database.models import TaskExecutionLog
import datetime

router = APIRouter()


@router.post("/tasks/callback")
async def task_callback(
        log_id: int = Body(...),
        status: int = Body(...),  # 2-执行中, 3-完成, 4-失败
        result: dict = Body(None),
        error_msg: str = Body(None)
):
    """
    子服务执行完任务后，调用此接口更新状态
    """
    db = SessionLocal()
    try:
        log = db.query(TaskExecutionLog).filter(TaskExecutionLog.id == log_id).first()
        if not log:
            return {"code": 404, "msg": "Log not found"}

        log.status = status
        if status == 2:  # 开始执行
            log.start_time = datetime.datetime.now()
        elif status in [3, 4]:  # 执行结束
            log.end_time = datetime.datetime.now()
            log.result = result
            log.error_info = error_msg

        db.commit()
        return {"code": 200, "msg": "状态更新成功"}
    finally:
        db.close()