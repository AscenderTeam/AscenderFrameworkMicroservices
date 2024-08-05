from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from plugins.microservices.backends.rabbitmq import RabbitMQDriver


class LiveConnections(dict[str, "RabbitMQDriver"]):
    default_connection: str = None
    
    def select_default(self, key: str):
        if not self.get(key, None):
            raise KeyError(f"Key {key} not found to set default connection")
        self.default_connection = key