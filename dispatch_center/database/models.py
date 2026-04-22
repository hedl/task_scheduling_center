# models.py
from sqlalchemy import Column, Integer, BigInteger, String, SmallInteger, DateTime, JSON, Text, Index
from sqlalchemy.orm import declarative_base  # 使用新的导入方式
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

# 使用新的方式创建 Base
Base = declarative_base()


class TaskQueue(Base):
    """任务队列表 ORM 模型"""
    __tablename__ = "task_queue"

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 任务基本信息
    task_name = Column(String(255), nullable=False, comment='任务名称')
    task_type = Column(String(50), nullable=True, comment='任务类型')
    task_state = Column(SmallInteger, nullable=False, default=0,
                        comment='任务状态：0-待执行，1-执行中，2-成功，3-失败，4-取消')

    # 时间字段
    start_time = Column(DateTime, nullable=True, comment='开始执行时间')
    finish_time = Column(DateTime, nullable=True, comment='完成执行时间')
    create_date = Column(DateTime, nullable=False, default=func.now(), comment='创建时间')
    update_date = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment='更新时间')

    # 数据字段
    task_param = Column(JSON, nullable=True, comment='任务执行参数（查询条件）')
    error_msg = Column(Text, nullable=True, comment='错误信息')
    remark_json = Column(JSON, nullable=True, comment='其他备注信息（JSON格式）')

    # 索引定义
    __table_args__ = (
        Index('idx_create_date', 'create_date'),
        Index('idx_state_create', 'task_state', 'create_date'),
        Index('idx_task_state', 'task_state'),
        Index('idx_task_type', 'task_type'),
        {'comment': '任务队列表'}
    )

    # 任务状态常量
    STATE_PENDING = 0  # 待执行
    STATE_RUNNING = 1  # 执行中
    STATE_SUCCESS = 2  # 成功
    STATE_FAILED = 3  # 失败
    STATE_CANCELLED = 4  # 取消

    # 状态映射
    STATE_MAP = {
        STATE_PENDING: '待执行',
        STATE_RUNNING: '执行中',
        STATE_SUCCESS: '成功',
        STATE_FAILED: '失败',
        STATE_CANCELLED: '取消'
    }

    def __repr__(self):
        return f"<TaskQueue(id={self.id}, task_name='{self.task_name}', task_state={self.task_state})>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'task_name': self.task_name,
            'task_type': self.task_type,
            'task_state': self.task_state,
            'task_state_name': self.get_state_name(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'finish_time': self.finish_time.isoformat() if self.finish_time else None,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'update_date': self.update_date.isoformat() if self.update_date else None,
            'task_param': self.task_param,
            'error_msg': self.error_msg,
            'remark_json': self.remark_json,
        }

    def get_state_name(self) -> str:
        """获取状态名称"""
        return self.STATE_MAP.get(self.task_state, '未知')

    def is_pending(self) -> bool:
        """是否为待执行状态"""
        return self.task_state == self.STATE_PENDING

    def is_running(self) -> bool:
        """是否为执行中状态"""
        return self.task_state == self.STATE_RUNNING

    def is_success(self) -> bool:
        """是否为成功状态"""
        return self.task_state == self.STATE_SUCCESS

    def is_failed(self) -> bool:
        """是否为失败状态"""
        return self.task_state == self.STATE_FAILED

    def is_cancelled(self) -> bool:
        """是否为取消状态"""
        return self.task_state == self.STATE_CANCELLED

    def can_execute(self) -> bool:
        """是否可以执行（待执行状态）"""
        return self.task_state == self.STATE_PENDING

    def can_retry(self) -> bool:
        """是否可以重试（失败状态）"""
        return self.task_state == self.STATE_FAILED

    def start_execute(self) -> None:
        """标记任务开始执行"""
        self.task_state = self.STATE_RUNNING
        self.start_time = datetime.now()

    def finish_success(self, result_data: Optional[Dict] = None) -> None:
        """标记任务执行成功"""
        self.task_state = self.STATE_SUCCESS
        self.finish_time = datetime.now()
        if result_data:
            self.remark_json = result_data

    def finish_failed(self, error_msg: str) -> None:
        """标记任务执行失败"""
        self.task_state = self.STATE_FAILED
        self.finish_time = datetime.now()
        self.error_msg = error_msg

    def cancel(self) -> None:
        """取消任务"""
        self.task_state = self.STATE_CANCELLED
        self.finish_time = datetime.now()

    def get_query_conditions(self) -> Optional[Dict]:
        """获取查询条件（从 task_param 中解析）"""
        if self.task_param and 'conditions' in self.task_param:
            return self.task_param.get('conditions')
        return None

    def get_batch_size(self) -> int:
        """获取批量大小"""
        if self.task_param and 'batch_size' in self.task_param:
            return self.task_param.get('batch_size', 100)
        return 100