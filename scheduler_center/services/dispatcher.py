import datetime
import httpx
import random
from database.db import SessionLocal
from database.models import ChildService, TaskExecutionLog
from core.logger import logger


async def dispatch_pinduoduo_tasks(platform: str):
    db = SessionLocal()
    try:
        # 1. 获取店铺数据 (模拟)
        shops = [{"name": "店铺A", "uid": "pdd_001"}]

        # 2. 获取可用子服务
        workers = db.query(ChildService).filter(ChildService.status == 1).all()
        if not workers: return

        async with httpx.AsyncClient() as client:
            for shop in shops:
                worker = random.choice(workers)

                # --- [重点] 创建执行日志记录 ---
                exec_log = TaskExecutionLog(
                    task_name="pdd_crawl",
                    business_id=shop['uid'],
                    service_id=worker.id,
                    service_name=worker.service_name,
                    status=0,  # 初始状态
                    payload={"shop_uid": shop['uid'], "platform": platform}
                )
                db.add(exec_log)
                db.flush()  # 获取 exec_log.id 以便传递给子服务

                try:
                    # 分发时把 log_id 发给子服务，方便子服务回调
                    payload = exec_log.payload
                    payload["log_id"] = exec_log.id

                    resp = await client.post(f"{worker.base_url}/execute", json=payload)

                    if resp.status_code == 200:
                        exec_log.status = 1  # 分发成功
                        exec_log.dispatch_time = datetime.datetime.now()
                    else:
                        exec_log.status = 4
                        exec_log.error_info = f"子服务响应异常: {resp.status_code}"
                except Exception as e:
                    exec_log.status = 4
                    exec_log.error_info = f"无法连接子服务: {str(e)}"
                db.commit()
    finally:
        db.close()