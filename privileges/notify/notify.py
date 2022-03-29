import gc
from abc import ABC, abstractmethod
from typing import Type, Set, Callable, TypeVar, Any

from privileges.notify.callbacks import default_callback

Callback = TypeVar('Callback', bound=Callable[..., Any])


class Notifier(ABC):
    """Оповещатель родительских объектов по событию notify"""

    @staticmethod
    def _find_parent_objects(obj: object, parent_type: Type, parent_objects: Set[object]):
        """Ищет все ссылающиеся на obj объекты типа child_type"""
        refs = gc.get_referrers(obj)
        for parent_obj in refs:
            if isinstance(parent_obj, parent_type):
                parent_objects.add(parent_obj)
                Notifier._find_parent_objects(
                    obj=parent_obj,
                    parent_type=parent_type,
                    parent_objects=parent_objects
                )

    @staticmethod
    @abstractmethod
    def notify(callback: Callback = default_callback, *args: Any, **kwargs: Any):
        """Уведомляет все объекты, ссылающиеся на obj того же типа, что и obj, вызывая для них callback"""
        pass

    @staticmethod
    @abstractmethod
    def cm_notify(callback: Callback = default_callback, *args: Any, **kwargs: Any):
        """Тот же notify, только работающий с classmthod-ами"""
        pass

    @staticmethod
    @abstractmethod
    def ping(object_: object, callback: Callback, *args: Any, **kwargs: Any):
        """Пингует объект о том, что что-то надо сделать"""
        pass
