from asyncio import get_event_loop, AbstractEventLoop
from typing import Optional, Union

import aioredis
from aioredis import Redis


class RedisControllerMeta(type):

    def __init__(cls, name, bases, attrs):
        cls._host = 'localhost'
        cls._port = '6379'
        cls._attr = 'redis'
        super(RedisControllerMeta, cls).__init__(name, bases, attrs)

    @property
    def host(cls):
        return cls._host

    @host.setter
    def host(cls, value: str):
        if not isinstance(value, str):
            raise ValueError('host must be str')
        cls._host = value

    @property
    def port(cls):
        return cls._port

    @port.setter
    def port(cls, value: Union[int, str]):
        if not isinstance(value, str) or not isinstance(value, int):
            raise ValueError('port must be int-able str or int')
        cls._port = value

    @property
    def attr(self):
        return self._attr

    @attr.setter
    def attr(cls, value: str):
        if not isinstance(value, str):
            raise ValueError('attr must be str')
        cls._attr = value


class RedisController(metaclass=RedisControllerMeta):
    """Контроллер взаимодействия с Redis"""

    def __init__(self, redis_pool: Redis, loop: AbstractEventLoop = get_event_loop()):
        self._loop = loop
        self._redis = redis_pool

    @property
    def pool(self):
        return self._redis

    @property
    def loop(self):
        return self._loop

    def __repr__(self):
        return str(self._redis.address)

    @staticmethod
    async def get_redis_pool(
            db: int = 0
    ) -> Redis:
        """Возвращает подключенный инстанс Redis"""
        try:
            pool_string = 'redis://{}:{}'.format(RedisController.host, RedisController.port)
            redis = await aioredis.create_redis_pool(pool_string, db=db, encoding='utf-8')  # type: Redis
            print('Соединение с %s установлено', redis.address)
        except Exception as e:
            raise ConnectionRefusedError(
                'Ошибка при установке соединения с %s: %s' % ((RedisController.host, RedisController.port), e)
            )
        return redis

    @staticmethod
    async def close_redis_pool(redis: Optional[Redis]):
        """Отключает инстанс Redis"""
        if isinstance(redis, Redis) and not redis.closed:
            try:
                redis.close()
                await redis.wait_closed()
            except Exception as e:
                raise ValueError(
                    'Ошибка при попытке закрытия соединения с %s: %s' %
                    (redis.address, e)
                )
            else:
                print('Соединение с %s закрыто', redis.address)

    @classmethod
    async def connect(cls, db: int = 0, loop: AbstractEventLoop = get_event_loop()):
        pool = await RedisController.get_redis_pool(db=db)
        return cls(redis_pool=pool, loop=loop)

    async def disconnect(self):
        await RedisController.close_redis_pool(redis=self._redis)

    def setup(self, o: object):
        redis_controller = getattr(o, RedisController.attr, self)
        setattr(o, RedisController.attr, redis_controller)
