from functools import wraps
from typing import Any, Callable, Set

from privileges.notify import Notifier, Callback
from privileges.notify.callbacks import default_callback


class BlockingNotifier(Notifier):
    """
    Notifier, который обрабатывает блокирующие callbacks
    """

    @staticmethod
    def cm_notify(callback: Callback = default_callback, *args: Any, **kwargs: Any):
        def decorator(obj_method: Callable):
            @wraps(obj_method)
            def wrapper(*method_args: Any, **method_kwargs: Any):
                obj = obj_method(*method_args, **method_kwargs)
                BlockingNotifier.ping(callback, *args, **kwargs)

                parent_objects = set()  # type: Set[obj]
                BlockingNotifier._find_parent_objects(obj, obj.__class__, parent_objects)
                for ch_obj in parent_objects:
                    BlockingNotifier.ping(ch_obj, callback, *args, **kwargs)
                return obj

            return wrapper

        return decorator

    @staticmethod
    def ping(object_: object, callback: Callback, *args: Any, **kwargs: Any):
        callback(object_, *args, **kwargs)

    @staticmethod
    def notify(callback: Callback = default_callback, *args: Any, **kwargs: Any):
        def decorator(obj_method: Callable):
            @wraps(obj_method)
            def wrapper(obj: object, *method_args: Any, **method_kwargs: Any):
                result = obj_method(obj, *method_args, **method_kwargs)
                BlockingNotifier.ping(obj, callback, *args, **kwargs)

                parent_objects = set()  # type: Set[obj]
                BlockingNotifier._find_parent_objects(obj, obj.__class__, parent_objects)
                for ch_obj in parent_objects:
                    BlockingNotifier.ping(ch_obj, callback, *args, **kwargs)
                return result

            return wrapper

        return decorator
