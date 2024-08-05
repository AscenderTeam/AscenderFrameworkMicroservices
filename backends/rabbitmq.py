import json
from typing import Any, Optional
from aio_pika import Message, connect
from pydantic import BaseModel

from plugins.microservices.types.config import RabbitMQConnection


class RabbitMQDriver:
    def __init__(self, url: Optional[str] = None,
                 *,
                 host: str = "localhost",
                 port: int = 5672,
                 login: str = "guest",
                 password: str = "guest") -> None:
        self.url = url
        self.host = host
        self.port = port
        self.login = login
        self.password = password

        self.connection = None

    async def connect(self):
        self.connection = await connect(self.url,
                                        host=self.host, port=self.port,
                                        login=self.login, password=self.password)

    async def disconnect(self):
        await self.connection.close()

    async def generate_channel(self, num: int | None = None):
        return await self.connection.channel(num)

    async def publish(self, body: Any | BaseModel, *, channel_id: int | None = None,
                      exchange: str = "",
                      routing_key: str = ""):
        channel = await self.generate_channel(channel_id)

        _exchange = await channel.get_exchange(exchange) if exchange != "" else channel.default_exchange

        if isinstance(body, BaseModel):
            body = body.model_dump_json()

        if not isinstance(body, (str, bytes)):
            body = json.dumps(
                body,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")

        if not isinstance(body, bytes):
            body = body.encode("utf-8")
        
        return await _exchange.publish(Message(body), routing_key=routing_key)


async def initialize(connection: RabbitMQConnection):
    url = connection.get("url", None)
    _host = connection.get("host", "localhost")
    _port = connection.get("port", 5672)
    _login = connection.get("login", "guest")
    _password = connection.get("password", "guest")

    driver = RabbitMQDriver(
        url, host=_host, password=_password, port=_port, login=_login)

    await driver.connect()
    return driver
