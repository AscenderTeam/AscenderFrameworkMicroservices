from datetime import timedelta
from typing import Any

from requests import delete
from plugins.microservices.backends.redis import RedisDriver
from plugins.microservices.exceptions.connections import UnsupportedConnectionError
from plugins.microservices.types.connections import LiveConnections


class RedisEngine:
    def __init__(self, connections: LiveConnections) -> None:
        self.connections = connections
    
    async def get(self, key: str, connection: str | None = None) -> Any | None:
        if not connection:
            if not (_connection := self.connections.get_default()):
                raise KeyError("There is no active connections!")
        
        else:
            if not (_connection := self.connections[connection]):
                return await self.get(key)
        
        if not isinstance(_connection, RedisDriver):
            raise UnsupportedConnectionError("Unsupported connection"\
                                             f"Expected RedisDriver, got {_connection.__class__.__name__}")

        return await _connection.get(key)
    
    async def set(self, key: str, value: str, ttl: float | timedelta | None = None, 
                  keepttl: bool = False,
                  connection: str | None = None):
        if not connection:
            if not (_connection := self.connections.get_default()):
                raise KeyError("There is no active connections!")
        
        else:
            if not (_connection := self.connections[connection]):
                return await self.get(key)
        
        if not isinstance(_connection, RedisDriver):
            raise UnsupportedConnectionError("Unsupported connection"\
                                             f"Expected RedisDriver, got {_connection.__class__.__name__}")

        return await _connection.set(key, value, 
                                     ex=ttl, keepttl=keepttl)
    
    async def get_all(self, tablename: str, connection: str | None = None) -> list[Any]:
        if not connection:
            if not (_connection := self.connections.get_default()):
                raise KeyError("There is no active connections!")
        
        else:
            if not (_connection := self.connections[connection]):
                return await self.get_all(tablename)
        
        if not isinstance(_connection, RedisDriver):
            raise UnsupportedConnectionError("Unsupported connection"\
                                             f"Expected RedisDriver, got {_connection.__class__.__name__}")
        matches = []
        cursor = b'0'

        while cursor:
            cursor, partial_keys = await _connection.connection.scan(cursor, match=f"{tablename}:*")
            matches.extend(partial_keys)

        
        values = []
        for match in matches:
            values.append(await _connection.get(match))
        
        return values
    
    async def delete(self, tablename: str, key: str | list[str], connection: str | None = None):
        if not connection:
            if not (_connection := self.connections.get_default()):
                raise KeyError("There is no active connections!")
        
        else:
            if not (_connection := self.connections[connection]):
                return await self.get_all(tablename)
        
        if not isinstance(_connection, RedisDriver):
            raise UnsupportedConnectionError("Unsupported connection"\
                                             f"Expected RedisDriver, got {_connection.__class__.__name__}")
        if isinstance(key, str):
            await _connection.connection.delete(f"{tablename}:{key}")
            return None
        
        keys = [f"{tablename}:{k}" for k in key]
        await _connection.connection.delete(*keys)
        return None