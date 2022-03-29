from asyncio import get_event_loop, AbstractEventLoop
from typing import Optional

import aioredis
from aioredis import Redis


class RedisControllerMeta(type):

    def __init__(cls, name, bases, attrs):
        super(RedisControllerMeta, cls).__init__(name, bases, attrs)


class RedisController(metaclass=RedisControllerMeta):
    """Контроллер взаимодействия с Redis"""
    HOST = 'localhost'
    PORT = '6379'
    ATTR = 'redis'

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
            pool_string = 'redis://{}:{}'.format(RedisController.HOST, RedisController.PORT)
            redis = await aioredis.create_redis_pool(pool_string, db=db, encoding='utf-8')  # type: Redis
            print('Соединение с %s установлено', redis.address)
        except Exception as e:
            raise ConnectionRefusedError(
                'Ошибка при установке соединения с %s: %s' % ((RedisController.HOST, RedisController.PORT), e)
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
        redis_controller = getattr(o, RedisController.ATTR, self)
        setattr(o, RedisController.ATTR, redis_controller)
