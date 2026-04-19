from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

# 任务配置表
class TaskConfig(Base):
    __tablename__ = "task_config"
    id = Column(Integer, primary_key=True)
    # 任务的唯一标识（例如：pdd_order_sync）。
    task_name = Column(String(100), unique=True)
    # 标准的 Cron 表达式（例如：0 0 * * * 表示每天凌晨执行），用来定义执行频率。
    cron_expr = Column(String(50))
    # 业务分类（例如：pinduoduo）
    platform = Column(String(50))
    # 开关控制 (is_active)：如果某个平台（如拼多多）接口维护，你只需要把 is_active 改成 0，调度中心就会自动停止下发该平台的任务。
    is_active = Column(Integer, default=1)


# 子服务/节点注册表
class ChildService(Base):
    __tablename__ = "child_services"
    id = Column(Integer, primary_key=True)
    # 节点的名称
    service_name = Column(String(100))
    # 子服务的 API 入口（例如：http://192.168.1.50:8001）
    base_url = Column(String(255))
    # 节点的健康状态。如果某个子服务宕机，状态变为 0，调度中心就不会再给它发任务。
    status = Column(Integer, default=1)


# 任务执行流水表
class TaskExecutionLog(Base):
    __tablename__ = "task_execution_logs"

    id = Column(Integer, primary_key=True)
    # 关联任务配置
    task_name = Column(String(100))
    # 具体的业务标识（如：店铺名称/唯一ID）
    business_id = Column(String(100))
    # 关联子服务
    service_id = Column(Integer)
    service_name = Column(String(100))

    # 状态：0-待分配, 1-分发成功, 2-执行中, 3-执行成功, 4-执行失败
    status = Column(Integer, default=0)

    # 时间追踪
    dispatch_time = Column(DateTime, default=datetime.datetime.now)  # 分配时间
    start_time = Column(DateTime, nullable=True)  # 子服务真正开始跑的时间
    end_time = Column(DateTime, nullable=True)  # 结束时间

    # 详情
    payload = Column(JSON)  # 发送给子服务的原始参数
    result = Column(JSON)  # 子服务返回的结果
    error_info = Column(Text)  # 失败时的堆栈信息


class TaskQueue(Base):
    __tablename__ = "task_queue"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_name = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=False)
    business_id = Column(String(100), nullable=False)

    # 任务内容
    task_payload = Column(JSON, nullable=False)

    # 状态与优先级
    priority = Column(Integer, default=0)
    status = Column(Integer, default=0)  # 0:Pending, 1:Running, 2:Success, 3:Failed

    # 重试逻辑
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # 锁标记
    lock_service_id = Column(Integer, nullable=True)
    locked_at = Column(DateTime, nullable=True)

    # 幂等键 (防止重复)
    idempotency_key = Column(String(128), unique=True, nullable=True)

    execute_time = Column(DateTime, nullable=True)

