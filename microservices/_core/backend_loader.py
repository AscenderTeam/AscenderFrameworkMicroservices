from typing import Any
from microservices.typehints.types import ControllerModule
from microservices._core.consume_executor import ConsumeExecutor
from microservices.backends.rabbitmq import RabbitMQDriver
from microservices.types.channels import ControllerChannel
from microservices.types.config import RabbitMQConnection
from importlib import import_module

async def load_backends(connections: dict[str, RabbitMQConnection]):
    live_connections: dict[str, RabbitMQDriver] = {}
    
    for name, connection in connections.items():
        driver_module = import_module(connection["driver"])
        
        live_connections[name] = await driver_module.initialize(connection)
    
    return live_connections


async def prepare_channels(live_connections: dict[str, RabbitMQDriver], controllers: dict[str, ControllerModule]):
    _channels = {}
    for name, config in controllers.items():
        controller_channels: list[ControllerChannel] | None = config.get("plugin_configs", {}).get("microservices", None)

        if not controller_channels:
            continue

        for controller_channel in controller_channels:
            if controller_channel.connection:
                connection = live_connections.get(controller_channel.connection, None)

                if not connection:
                    # TODO: Custom exception
                    raise ValueError("Connection doesn't exist")

            _channels[name] = (controller_channel, config)
    
    return _channels


async def initialize_channels(consume_executor: ConsumeExecutor, _channels: dict[str, tuple[ControllerChannel, ControllerModule]]):
    for name, channel in _channels.items():
        await consume_executor.define_driver_add((name, channel[1]), channel[0])


async def inject_channels(consume_executor: ConsumeExecutor, active_controllers: dict[str, object]):
    for controller_name, channels in consume_executor.channels.items():
        _controller = active_controllers.get(controller_name, None)
        if not _controller:
            continue

        for channel in channels:
            setattr(_controller, channel.channel.__name__.lower(), channel._channel)


async def load_stores(distributor: Any, live_connections: dict[str, RabbitMQDriver], consume_executor: ConsumeExecutor):
    connections_storage = distributor.create_base_store(live_connections)
    
    channel_storages = {}
    for controller_name, channels in consume_executor.channels.items():
        for channel in channels:
            channel_storages[f"{controller_name.lower()}.{channel.channel.__name__.lower()}"] = distributor.create_base_store(channel._channel)
    
    return connections_storage, channel_storages