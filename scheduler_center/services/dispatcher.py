import datetime
import httpx
import random
from database.db import SessionLocal
from database.models import ChildService, TaskExecutionLog
from core.logger import logger
import uuid7gen


async def dispatch_pinduoduo_tasks(platform: str):
    db = SessionLocal()
    try:
        # 1. 获取店铺数据 (模拟)
        shops = {
            "FXTM-WBO-25028": ["1234567832", "12234575656"],
            "FXTM-WBO-25029": ["2234567890", "13234567890"],
            "FXTM-WBO-25030": ["3234567891", "14234567891"],
            "FXTM-WBO-25031": ["4234567892", "15234567892"],
            "FXTM-WBO-25032": ["5234567893", "16234567893"],
            "FXTM-WBO-25033": ["6234567894", "17234567894"],
            "FXTM-WBO-25034": ["7234567895", "18234567895"],
            "FXTM-WBO-25035": ["8234567896", "19234567896"],
            "FXTM-WBO-25036": ["9234567897", "20234567897"],
            "FXTM-WBO-25037": ["0234567898", "21234567898"],
            "FXTM-WBO-25038": ["1134567899", "22234567899"],
            "FXTM-WBO-25039": ["2134567800", "23234567900"],
            "FXTM-WBO-25040": ["3134567801", "24234567901"],
            "FXTM-WBO-25041": ["4134567802", "25234567902"],
            "FXTM-WBO-25042": ["5134567803", "26234567903"],
            "FXTM-WBO-25043": ["6134567804", "27234567904"],
            "FXTM-WBO-25044": ["7134567805", "28234567905"],
            "FXTM-WBO-25045": ["8134567806", "29234567906"],
            "FXTM-WBO-25046": ["9134567807", "30234567907"],
            "FXTM-WBO-25047": ["0144567808", "31234567908"]
        }

        # 2. 获取可用子服务
        workers = db.query(ChildService).filter(ChildService.status == 1).all()
        if not workers: return

        async with httpx.AsyncClient() as client:
            for shop_unique_mark,goods_id in shops.items():
                my_uuid = uuid7gen.uuid7()
                worker = random.choice(workers)

                # --- [重点] 创建执行日志记录 ---
                exec_log = TaskExecutionLog(
                    task_name= "pdd_crawl",
                    business_id= my_uuid,
                    service_id= worker.id,
                    service_name= worker.service_name,
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