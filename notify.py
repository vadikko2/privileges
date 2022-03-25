import gc
from functools import wraps
from typing import Type, Set, Callable, TypeVar, Any

Callback = TypeVar('Callback', bound=Callable[..., Any])


class Notifier:
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
    def notify(callback: Callback, *args: Any, **kwargs: Any):
        """Уведомляет все объекты, ссылающиеся на obj того же типа, что и obj, вызывая для них callback"""

        def decorator(obj_method: Callable):
            @wraps(obj_method)
            def wrapper(obj: object, *method_args: Any, **method_kwargs: Any):
                result = obj_method(obj, *method_args, **method_kwargs)
                Notifier.ping(obj, callback, *args, **kwargs)

                parent_objects = set()  # type: Set[obj]
                Notifier._find_parent_objects(obj, obj.__class__, parent_objects)
                for ch_obj in parent_objects:
                    Notifier.ping(ch_obj, callback, *args, **kwargs)
                return result

            return wrapper

        return decorator

    @staticmethod
    def ping(object_: object, callback: Callback, *args: Any, **kwargs: Any):
        """Пингует объект о том, что что-то надо сделать"""
        callback(object_, *args, **kwargs)
