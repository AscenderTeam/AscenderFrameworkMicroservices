from typing import TYPE_CHECKING, Any
from core.plugins.plugin_injector import PluginInjector
from core.types import ControllerModule
from plugins.microservices._core.consume_executor import ConsumeExecutor
from plugins.microservices.backends.rabbitmq import RabbitMQDriver
from plugins.microservices.backends.redis import RedisDriver
from plugins.microservices.types.channels import ControllerChannel
from plugins.microservices.types.config import RabbitMQConnection, RedisConnection
from importlib import import_module

from plugins.microservices.types.connections import LiveConnections

if TYPE_CHECKING:
    from plugins.microservices.types.http_waypoint import HTTPWaypoint

async def load_backends(connections: dict[str, RabbitMQConnection | RedisConnection]):
    live_connections = LiveConnections()
    
    for name, connection in connections.items():
        driver_module = import_module(f"plugins.{connection['driver']}")
        
        live_connections[name] = await driver_module.initialize(connection)
    
    return live_connections


async def prepare_channels(live_connections: LiveConnections, controllers: dict[str, ControllerModule]):
    _channels = {}
    for name, config in controllers.items():
        controller_channels: list[ControllerChannel] | None

        if not (controller_channels := config.get("plugin_configs", {}).get("microservices", None)):
            continue

        for controller_channel in controller_channels:
            if controller_channel.connection:
                connection = live_connections.get(controller_channel.connection, None)

                if not connection:
                    # TODO: Custom exception
                    raise ValueError("Connection doesn't exist")
                
                if isinstance(connection, RedisDriver):
                    raise TypeError("Redis connection isn't supported in channels yet. (WIP)")

            _channels[controller_channel.channel.__name__] = (controller_channel, config)
    
    return _channels


# def prepare_httpwaypoints(controllers: dict[str, ControllerModule]):
#     from plugins.microservices.types.http_waypoint import HTTPWaypoint
    
#     _waypoints = {}
#     for name, config in controllers.items():
#         controller_waypoints: list[HTTPWaypoint] | None

#         if not (controller_waypoints := config.get("plugin_configs", {}).get("waypoints", None)):
#             continue

#         for controller_waypoint in controller_waypoints:
#             _waypoints[controller_waypoint.waypoint.__name__] = controller_waypoint
    
#     return _waypoints


async def initialize_channels(consume_executor: ConsumeExecutor, _channels: dict[str, tuple[ControllerChannel, ControllerModule]]):
    for name, channel in _channels.items():
        await consume_executor.define_driver_add((name, channel[1]), channel[0])

def initialize_waypoints(_waypoints: list["HTTPWaypoint"],
                         injector: PluginInjector):
    for waypoint in _waypoints:
        waypoint.define_waypoint(injector)

async def disable_waypoint_shared_connectors(_waypoints: dict[str, "HTTPWaypoint"]):
    for _, waypoint in _waypoints.items():
        await waypoint.close_waypoint()

# async def 