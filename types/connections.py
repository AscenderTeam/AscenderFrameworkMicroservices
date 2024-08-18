# from __future__ import annotations
# from typing import TYPE_CHECKING


from plugins.microservices.backends.rabbitmq import RabbitMQDriver
from plugins.microservices.backends.redis import RedisDriver
# if TYPE_CHECKING:


class LiveConnections(dict[str, RabbitMQDriver | RedisDriver]):
    default_connection: str = None
    
    def select_default(self, key: str):
        # if not self.get(key, None):
        #     raise KeyError(f"Key {key} not found to set default connection")
        self.default_connection = key
    
    def get_default(self):
        return self[self.default_connection]