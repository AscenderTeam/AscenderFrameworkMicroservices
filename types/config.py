from typing import Literal, NotRequired, Optional, TypedDict


class RabbitMQConnection(TypedDict):
    driver: Literal["microservices.backends.rabbitmq"]
    url: Optional[str]
    host: str
    port: int
    login: str
    password: str

    default_queue: Optional[str]


class RedisConnection(TypedDict):
    driver: Literal["microservices.backends.redis"]
    url: NotRequired[Optional[str]]
    host: NotRequired[str]
    port: NotRequired[int]
    password: NotRequired[str]
    db: NotRequired[str | int]


class MainConfig(TypedDict):
    connections: dict[str, RabbitMQConnection | RedisConnection]
    default_connection: str