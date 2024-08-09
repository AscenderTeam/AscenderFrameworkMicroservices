from typing import Optional
from redis.asyncio import Redis

from plugins.microservices.types.config import RedisConnection


class RedisDriver:
    def __init__(self, url: Optional[str] = None,
                 *,
                 host: str = "localhost",
                 port: int = 6379,
                 password: Optional[str] = None,
                 db: str | int = 0) -> None:
        self.url = url
        self.host = host
        self.port = port
        self.password = password
        self.db = db

        self.connection = None

    async def connect(self):
        if self.url:
            self.connection = await Redis.from_url(self.url)
            return
        
        self.connection = await Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password
        )

    async def disconnect(self):
        await self.connection.close()

    @property
    def hset(self):
        return self.connection.hset
    
    @property
    def set(self):
        return self.connection.set
    
    @property
    def get(self):
        return self.connection.get


async def initialize(connection: RedisConnection):
    url = connection.get("url", None)
    _host = connection.get("host", "localhost")
    _port = connection.get("port", 6379)
    _password = connection.get("password", None)
    _db = connection.get("db", 0)

    driver = RedisDriver(
        url, host=_host, password=_password, port=_port, db=_db)

    await driver.connect()
    return driver
