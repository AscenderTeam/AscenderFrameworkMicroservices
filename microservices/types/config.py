from typing import Literal, Optional, TypedDict


class RabbitMQConnection(TypedDict):
    driver: Literal["src.microservices.backends.rabbitmq"]
    url: Optional[str]
    host: str
    port: int
    login: str
    password: str

    default_queue: Optional[str]


class MainConfig(TypedDict):
    connections: dict[str, RabbitMQConnection]
    default_connection: str