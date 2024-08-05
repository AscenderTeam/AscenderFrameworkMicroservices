from typing import Any, Literal
from aio_pika.channel import AbstractChannel, AbstractExchange


class RQControllerExchanger:
    def __init__(self, name: str = "", 
                 exchange_type: Literal["fanout", "direct", "headers", "topic"] = "fanout", *,
                 durable: bool = False, 
                 auto_delete: bool = False, 
                 internal: bool = False, 
                 passive: bool = False, 
                 arguments: dict[str, Any] | None = None, 
                 timeout: float | int | None = None) -> None:
        self.name = name
        self.exchange_type = exchange_type
        self.durable = durable
        self.auto_delete = auto_delete
        self.internal = internal
        self.passive = passive
        self.arguments = arguments
        self.timeout = timeout
    
    async def build(self, channel: AbstractChannel):
        exchanger = await channel.declare_exchange(self.name, self.exchange_type, 
                                                   durable=self.durable,
                                                   auto_delete=self.auto_delete,
                                                   internal=self.internal,
                                                   passive=self.passive,
                                                   arguments=self.arguments,
                                                   timeout=self.timeout)
        
        return exchanger
    

class RQControllerQueue:
    def __init__(self, name: str | None = None, *, 
                 durable: bool = False, 
                 exclusive: bool = False, 
                 passive: bool = False, 
                 auto_delete: bool = False, 
                 arguments: dict[str, Any] | None = None, 
                 timeout: float | int | None = None) -> None:
        self.name = name
        self.durable = durable
        self.exclusive = exclusive
        self.passive = passive
        self.auto_delete = auto_delete
        self.arguments = arguments
        self.timeout = timeout
    
    async def build(self, channel: AbstractChannel, exchanger: AbstractExchange,
                    routing_key: str | None = None):
        queue = await channel.declare_queue(self.name, durable=self.durable,
                                            exclusive=self.exclusive,
                                            passive=self.passive, auto_delete=self.auto_delete,
                                            arguments=self.arguments, timeout=self.timeout)
        
        await queue.bind(exchanger, routing_key=routing_key)
        return queue