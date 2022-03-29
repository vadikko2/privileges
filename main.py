from asyncio import get_event_loop
from typing import Coroutine

from privileges import Privilege, EventsBitValues
from privileges.bits import Bit
from privileges.notify.async_notifier import AsyncNotifier
from privileges.notify.block_notifier import BlockingNotifier
from privileges.redis.redis import RedisController


async def save_redis_callback(o: Privilege):
    redis_controller = getattr(o, RedisController.attr, None)
    if not isinstance(redis_controller, RedisController):
        raise AttributeError('Ошибка получения RedisController из объекта %r' % o)
    if redis_controller.pool.closed:
        raise ConnectionError('Отсутствует подключение к %r' % redis_controller)

    try:
        await redis_controller.pool.set(o.uid, int(o))
    except Exception as e:
        raise ValueError('Ошибка при записи %r по ключу %s: %s' % (o, o.uid, e))
    else:
        print('Сохранено %r по ключу %s' % (o, o.uid))


def print_callback(o: Privilege):
    print('Обновление объекта %r' % o)


class NotifyingPrivileges(Privilege):
    """
    Реализует уведомление всех родительских объектов об изменении привилегии
    """

    @BlockingNotifier.notify(callback=print_callback)
    def set(self, key, value) -> None:
        """Уведомляет всех родителей при внесении изменений в привилегию"""
        return super(NotifyingPrivileges, self).set(key, value)


class AsyncRedisPrivileges(Privilege):
    """
    Расширяет интерфейс асинхронными вызовами + добавляет сохранение в Redis при изменении инстанса
    """

    @classmethod
    @AsyncNotifier.cm_notify(callback=save_redis_callback)
    def async_init(cls, *args, redis: RedisController, **kwargs) -> Coroutine:
        """Создает инстанс и записывает значение в Redis"""
        instance = cls(*args, **kwargs)
        redis.setup(instance)
        return instance

    @AsyncNotifier.notify(callback=save_redis_callback)
    def set(self, key, value) -> Coroutine:
        """Уведомляет всех родителей при внесении изменений в привилегию"""
        return super(AsyncRedisPrivileges, self).set(key, value)

    @classmethod
    @AsyncNotifier.cm_notify(callback=save_redis_callback)
    def async_create_privilege(cls, *args, redis: RedisController, **kwargs) -> Coroutine:
        """Создает инстанс и записывает значение в Redis"""
        instance = AsyncRedisPrivileges.create_privilege(*args, **kwargs)
        redis.setup(instance)
        return instance

    @classmethod
    @AsyncNotifier.cm_notify(callback=save_redis_callback)
    def async_from_int(cls, *args, redis: RedisController, **kwargs) -> Coroutine:
        """Создает инстанс из int и записывает значение в Redis"""
        instance = AsyncRedisPrivileges.from_int(*args, **kwargs)
        redis.setup(instance)
        return instance


async def main():
    RedisController.host = 'localhost'

    redis = await RedisController.connect(db=5)

    root = await AsyncRedisPrivileges.async_init(
        bits=[None, Bit.true, Bit.false, None, Bit.true, Bit.false, Bit.true, None, None, Bit.true],
        uid='ROOT', redis=redis
    )

    # Наследуемся от root и переопределяем привилегии
    first_child = await AsyncRedisPrivileges.async_create_privilege(
        privileges={key: Bit.true for key in EventsBitValues},
        parent_privileges=root, uid='FIRST', redis=redis
    )

    # Наследуемся от root, но не переопределяем привилегии
    empty_child = await AsyncRedisPrivileges.async_create_privilege(
        {}, parent_privileges=root, uid='EMPTY', redis=redis
    )
    assert empty_child == root  # True

    # Наследуем от first_child и переопределяем парочку привилегий
    second_child = await AsyncRedisPrivileges.async_create_privilege(
        {key: Bit.false for key in [
            EventsBitValues.inVis,
            EventsBitValues.inVid,
            EventsBitValues.inMsg
        ]}, parent_privileges=first_child, uid='SECOND', redis=redis
    )

    await root.set(EventsBitValues.inVis, Bit.false)
    assert first_child.get(EventsBitValues.outSts) is second_child.get(EventsBitValues.outSts)

    await second_child.set(EventsBitValues.outMsg, Bit.false)

    from_int = await AsyncRedisPrivileges.async_from_int(265, uid='FROM INT', redis=redis)
    assert root == from_int

    await redis.disconnect()


if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())
