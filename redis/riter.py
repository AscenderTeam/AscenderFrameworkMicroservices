from typing import Generic, TypeVar
from plugins.microservices.redis.singleton import RedisEngineSingleton

T = TypeVar("T")


class RIterable(Generic[T], list[T]):
    entity_type: T | None = None

    def set_redis_type(self, entity: T):
        self.entity_type = entity

    async def delete(self):
        redis_engine = RedisEngineSingleton()

        await redis_engine.delete(self.entity_type._entityname.default, [getattr(result, self.entity_type._primaryfield.default) 
                                                                 for result in self], self.entity_type._connection.default)
    
    async def first(self):
        try:
            return self[0]
        except IndexError:
            return None