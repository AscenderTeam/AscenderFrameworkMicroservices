from typing import Optional

from aio_pika import Exchange, IncomingMessage
from microservices.typehints.types import ControllerModule
from microservices.context import MessageContext
from microservices.handler import Channel
from microservices.types.modules import RQControllerExchanger, RQControllerQueue


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
    
    def define_channel(self, config: ControllerModule, exchanger: Exchange):
        services = config.get('services', {})
        repository = config.get('repository', None)
        repository_entities = config.get('repository_entities', {})
        if repository is not None:
            repository = repository(**repository_entities)
        service_instances = {}
        for key, service in services.items():
            service._loader = self
            service_instances[key+"_service"] = service(repository=repository)

        self._channel = self.channel(**service_instances)
        self._channel.exchange = exchanger
        self._channel.routing_key = self.routing_key
        self._exchanger = exchanger

    async def callback(self, message: IncomingMessage):
        message_context = MessageContext(message, self._exchanger, self._channel)
        if self.auto_acknowledgement:
            async with message.process():
                return await self._channel.handle(message_context)
        
        return await self._channel.handle(message_context)