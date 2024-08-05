from typing import Optional

from aio_pika import Exchange, IncomingMessage
from core.registries.service import ServiceRegistry
from core.types import ControllerModule
from plugins.microservices.context import MessageContext
from plugins.microservices.handler import Channel
from plugins.microservices.parsers.consume_handle import ConsumeHandleParser
from plugins.microservices.types.modules import RQControllerExchanger, RQControllerQueue


class ControllerChannel:
    def __init__(self, channel: type[Channel], *, 
                 routing_key: str = '',
                 queue: Optional[RQControllerQueue] = None,
                 enable_controller_exchanger: bool = False,
                 controller_exchanger: Optional[RQControllerExchanger] = None,
                 auto_acknowledgement: bool = True,
                 connection: Optional[str] = None) -> None:
        self.channel = channel
        self.routing_key = routing_key
        self.queue = queue
        self.enable_controller_exchanger = enable_controller_exchanger
        self.controller_exchanger = controller_exchanger
        self.auto_acknowledgement = auto_acknowledgement
        
        self.connection = connection
    
    def define_channel(self, exchanger: Exchange):
        service_registry = ServiceRegistry()
        
        _parameters = service_registry.get_parameters(self.channel)
        self._channel = self.channel(**_parameters)
        self._channel.exchange = exchanger
        self._channel.routing_key = self.routing_key
        self._exchanger = exchanger
        service_registry.add_singletone(self.channel, self._channel)

    async def callback(self, message: IncomingMessage):
        parser = ConsumeHandleParser(self._channel.handle)
        message_context = MessageContext(message, self._exchanger, self._channel)

        payload = [message_context]

        if body := parser(message_context.message.body.decode()):
            payload.append(body)

        if self.auto_acknowledgement:
            async with message.process():
                return await self._channel.handle(*payload)
        
        return await self._channel.handle(*payload)