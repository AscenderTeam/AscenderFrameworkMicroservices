from datetime import timedelta
from typing import Self, TypeVar
from pydantic import BaseModel, ConfigDict, PrivateAttr

from plugins.microservices.redis.riter import RIterable
from plugins.microservices.redis.singleton import RedisEngineSingleton


class RedisEntity(BaseModel):

    _entityname: str
    _primaryfield: str = "id"
    _connection: str | None = None

    @classmethod
    async def get(cls, id: int) -> Self | None:
        redis_engine = RedisEngineSingleton()
        if _result := await redis_engine.get(f"{cls._entityname.default}:{id}", cls._connection.default):
            return cls.model_validate_json(_result)
        
        return None
    
    @classmethod
    async def all(cls) -> RIterable[Self]:
        redis_engine = RedisEngineSingleton()
        
        _result = await redis_engine.get_all(cls._entityname.default, cls._connection.default)
        _response = RIterable([cls.model_validate_json(result) for result in _result])
        _response.set_redis_type(cls)
        return _response
    
    async def save(self, ttl: float | timedelta | None = None,
                   _keepttl: bool = False):
        redis_engine = RedisEngineSingleton()

        await redis_engine.set(f"{self._entityname}:{getattr(self, self._primaryfield)}", self.model_dump_json(),
                                         ttl, _keepttl,
                                         self._connection)
    
    async def delete(self):
        redis_engine = RedisEngineSingleton()

        await redis_engine.delete(self._entityname, getattr(self, self._primaryfield),
                                  self._connection)