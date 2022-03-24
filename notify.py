import gc
from typing import Type, Set, Callable


class Notifier:
    """Оповещатель родительских объектов по событию notify"""

    @staticmethod
    def _find_child_objects(obj: object, parent_type: Type, parent_objects: Set[object]):
        """Ищет все ссылающиеся на obj объекты типа child_type"""
        refs = gc.get_referrers(obj)
        for parent_obj in refs:
            if isinstance(parent_obj, parent_type):
                parent_objects.add(parent_obj)
                Notifier._find_child_objects(
                    obj=parent_obj,
                    parent_type=parent_type,
                    parent_objects=parent_objects
                )

    @staticmethod
    def notify(obj: object, parent_type: Type, callback: Callable):
        """Уведомляет все объекты, ссылающиеся на obj, вызывая для них callback"""
        Notifier.ping(object_=obj, callback=callback)
        parent_objects = set()  # type: Set[parent_type]
        Notifier._find_child_objects(obj, parent_type, parent_objects)
        for ch_obj in parent_objects:
            Notifier.ping(ch_obj, callback)

    @staticmethod
    def ping(object_: object, callback: Callable[[object], None]):
        """Пингует объект о том, что что-то надо сделать"""
        callback(object_)
