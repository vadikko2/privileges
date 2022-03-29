from asyncio import iscoroutinefunction
from functools import wraps
from typing import Any, Callable, Set

from privileges.notify import Notifier, Callback
from privileges.notify.callbacks import async_dfault_callback


class AsyncNotifier(Notifier):
    """
    Notifier, который обрабатывает await-able callbacks
    """

    @staticmethod
    def cm_notify(callback: Callback = async_dfault_callback, *args: Any, **kwargs: Any):
        def decorator(obj_method: Callable):
            @wraps(obj_method)
            async def wrapper(*method_args: Any, **method_kwargs: Any):
                if iscoroutinefunction(obj_method):
                    obj = await obj_method(*method_args, **method_kwargs)
                else:
                    obj = obj_method(*method_args, **method_kwargs)
                await AsyncNotifier.ping(obj, callback, *args, **kwargs)

                parent_objects = set()  # type: Set[obj]
                AsyncNotifier._find_parent_objects(obj, obj.__class__, parent_objects)
                for ch_obj in parent_objects:
                    await AsyncNotifier.ping(ch_obj, callback, *args, **kwargs)

                return obj

            return wrapper

        return decorator

    @staticmethod
    def notify(callback: Callback = async_dfault_callback, *args: Any, **kwargs: Any):
        def decorator(obj_method: Callable):
            @wraps(obj_method)
            async def wrapper(obj: object, *method_args: Any, **method_kwargs: Any):
                if iscoroutinefunction(obj_method):
                    result = await obj_method(obj, *method_args, **method_kwargs)
                else:
                    result = obj_method(obj, *method_args, **method_kwargs)
                await AsyncNotifier.ping(obj, callback, *args, **kwargs)

                parent_objects = set()  # type: Set[obj]
                AsyncNotifier._find_parent_objects(obj, obj.__class__, parent_objects)
                for ch_obj in parent_objects:
                    await AsyncNotifier.ping(ch_obj, callback, *args, **kwargs)

                return result

            return wrapper

        return decorator

    @staticmethod
    async def ping(object_: object, callback: Callback, *args: Any, **kwargs: Any):
        await callback(object_, *args, **kwargs)
