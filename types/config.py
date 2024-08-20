from datetime import timedelta
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


class InternalPrivacyConfig(TypedDict):
    enabled: bool
    secret_key: str
    token_lifetime: timedelta
    allowed_services: list[str]
    current_service_id: str


class MainConfig(TypedDict):
    connections: dict[str, RabbitMQConnection | RedisConnection]
    default_connection: str
    internal_privacy: NotRequired[InternalPrivacyConfig]