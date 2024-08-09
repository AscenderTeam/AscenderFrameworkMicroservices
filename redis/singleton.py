from asyncio import Lock
from plugins.microservices.exceptions.connections import UnsupportedConnectionError
from plugins.microservices.exceptions.uninitialized import UninitializedServer
from plugins.microservices.redis.engine import RedisEngine


class RedisEngineSingleton:
    _instance: RedisEngine | None = None
    # _lock: Lock = Lock()

    def __new__(cls, instance: RedisEngine | None = None) -> RedisEngine:
        # with cls._lock:
        if not cls._instance:
            if instance is None:
                raise UninitializedServer("Redis Engine is not initialized")
            cls._instance = instance
        
        return cls._instance