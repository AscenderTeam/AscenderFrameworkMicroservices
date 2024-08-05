from logging import getLogger
from core.types import ControllerModule
from plugins.microservices.backends.rabbitmq import RabbitMQDriver
from plugins.microservices.types.channels import ControllerChannel
from plugins.microservices.types.modules import RQControllerExchanger, RQControllerQueue


class ConsumeExecutor:
    def __init__(self, live_connections: dict[str, RabbitMQDriver], 
                 default_connection: dict[str, RabbitMQDriver]) -> None:
        self.live_connections = live_connections
        self.default_connection = default_connection
        self.logger = getLogger("ascender-plugins")
        self.__channels: dict[str, list[ControllerChannel]] = {}

    @property
    def channels(self):
        return self.__channels

    async def define_driver_add(self, controller: tuple[str, ControllerModule], controller_channel: ControllerChannel):
        connection = self.live_connections.get(controller_channel.connection, None) if controller_channel.connection else self.live_connections.get(self.default_connection)

        if not connection and controller_channel.connection:
            self.logger.warn(f"Connection {controller_channel.connection} was not found, using default connection...")
            connection = self.default_connection

        if isinstance(connection, RabbitMQDriver):
            await self.add_controller_rmq(controller, controller_channel, connection)

    async def add_controller_rmq(self, controller: tuple[str, ControllerModule], controller_channel: ControllerChannel, connection: RabbitMQDriver):
        
        if not isinstance(connection, RabbitMQDriver):
            # TODO: Implement custom exception
            raise ValueError("Wrong driver!")

        _channel = await connection.generate_channel()
        
        exchanger = await RQControllerExchanger(name="ascender_framework.root", exchange_type="direct").build(_channel)

        if controller_channel.enable_controller_exchanger:
            if controller_channel.controller_exchanger:
                exchanger = await controller_channel.controller_exchanger.build(_channel)
            else:
                exchanger = await RQControllerExchanger(name=controller[0], exchange_type="direct").build(_channel)
            
        queue = await controller_channel.queue.build(_channel, exchanger, controller_channel.routing_key) if controller_channel.queue else await RQControllerQueue().build(_channel, exchanger, controller_channel.routing_key)
        
        controller_channel.define_channel(exchanger)
        
        await queue.consume(controller_channel.callback, not controller_channel.auto_acknowledgement)

        if self.__channels.get(controller[0]):
            self.__channels[controller[0]].append(controller_channel)
        
        else:
            self.__channels[controller[0]] = [controller_channel]