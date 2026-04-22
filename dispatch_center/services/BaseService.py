from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from database.db import SessionLocal
from database.models import TaskQueue


class BaseService(ABC):
    """调度服务抽象基类 - 定义统一接口规范"""

    @abstractmethod
    def create_executor(self, executor_type: str) -> Any:
        """
        创建分发处理器（工厂方法）

        Args:
            executor_type: 分发类型，如 'export', 'import', 'process' 等

        Returns:
            分发处理器实例
        """
        pass

    @abstractmethod
    def _create_executor_impl(self, executor_type: str) -> Any:
        """
        子类实现具体分发处理器的创建逻辑

        Args:
            executor_type: 分发类型

        Returns:
            分发处理器实例
        """
        pass

    @abstractmethod
    def _build_task_param(self, executor: Any, custom_param: Optional[Dict] = None) -> Dict:
        """
        子类实现如何使用 executor 构建 task_param

        Args:
            executor: 分发处理器
            custom_param: 调用方传入的自定义参数

        Returns:
            构建好的任务参数字典
        """
        pass

    def execute(self, task_name: str, executor_type: str,
                task_type: Optional[str] = None,
                custom_param: Optional[Dict] = None) -> int:
        """
        将任务分发到队列

        Args:
            task_name: 任务名称
            executor_type: 分发类型
            task_type: 任务类型（可选）
            custom_param: 自定义参数（可选）

        Returns:
            新创建的任务ID
        """
        executor = self.create_executor(executor_type)
        task_param = self._build_task_param(executor, custom_param)

        task = TaskQueue(
            task_name=task_name,
            task_type=task_type or executor_type,
            task_param=task_param
        )

        db = SessionLocal()
        try:
            db.add(task)
            db.commit()
            db.refresh(task)
            return task.id
        finally:
            db.close()

    def get_task_status(self, task_id: int) -> Optional[Dict]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务信息字典，不存在则返回 None
        """
        db = SessionLocal()
        try:
            task = db.query(TaskQueue).filter(TaskQueue.id == task_id).first()
            return task.to_dict() if task else None
        finally:
            db.close()


class ServiceFactory:
    """服务工厂 - 用于实例化实现类"""

    _services = {}

    @classmethod
    def register(cls, name: str, service_class: type):
        """
        注册服务类

        Args:
            name: 服务名称
            service_class: 服务类（必须是 BaseService 的子类）
        """
        if not issubclass(service_class, BaseService):
            raise ValueError(f"{service_class} must be a subclass of BaseService")
        cls._services[name] = service_class

    @classmethod
    def get_service(cls, name: str) -> BaseService:
        """
        获取服务实例

        Args:
            name: 服务名称

        Returns:
            服务实例
        """
        if name not in cls._services:
            raise KeyError(f"Service '{name}' not registered")
        return cls._services[name]()

    @classmethod
    def list_services(cls) -> list:
        """列出所有已注册的服务名称"""
        return list(cls._services.keys())


def register_service(name: str):
    """服务注册装饰器"""
    def decorator(cls):
        ServiceFactory.register(name, cls)
        return cls
    return decorator