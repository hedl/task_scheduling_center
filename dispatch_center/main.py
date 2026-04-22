from services.impl.PddTaskImpl import PddTaskImpl
from services.BaseService import ServiceFactory
from tool.scheduled_trigger import scheduled_trigger
import time

# 注册并获取服务实例
ServiceFactory.register("pdd", PddTaskImpl)
pdd_task_impl = ServiceFactory.get_service("pdd")


@scheduled_trigger(second=0, minute=30, hour=8, task_impl=pdd_task_impl)
def daily_pdd_task(task_impl):
    """每天8点30分执行PDD任务分发"""
    print("触发PDD定时任务")
    task_id = task_impl.execute(
        task_name="PDD定时任务",
        executor_type="xxx"
    )
    print(f"任务已分发，ID: {task_id}")


if __name__ == "__main__":
    print("调度中心启动...")
    while True:
        time.sleep(1)