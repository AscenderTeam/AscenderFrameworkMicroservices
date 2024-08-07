from typing import TYPE_CHECKING
from core.application import Application
from core.plugins.plugin import Plugin
from core.types import ControllerModule
from plugins.microservices._core.backend_loader import disable_waypoint_shared_connectors, initialize_channels, initialize_waypoints, load_backends, prepare_channels, prepare_httpwaypoints
from plugins.microservices._core.consume_executor import ConsumeExecutor
from plugins.microservices.types.channels import ControllerChannel
from plugins.microservices.types.config import MainConfig
from plugins.microservices.types.connections import LiveConnections

if TYPE_CHECKING:
    from plugins.microservices.types.http_waypoint import HTTPWaypoint


class AscenderFrameworkMicroservices(Plugin):
    name: str = "ascender-framework-microservices"
    description: str = "Ascender Framework Microservices is the lightweight plugin for Ascender Framework starting from version 1.1.0 that allows Microservice integration using Redis/RabbitMQ/Kafka/TCP Transport"
    
    def __init__(self, config: MainConfig, use_http_waypoints: bool = False) -> None:
        self.config = config
        self.use_http_waypoints = use_http_waypoints

        self.default_connection = self.config["connections"][self.config["default_connection"]]
        self.connections = self.config["connections"]
        self.controllers: dict[str, ControllerModule] = {}
        self.active_controllers: dict[str, object] = {}
        self.loaded_channels: dict[str, tuple[ControllerChannel, ControllerModule]] = {}
        self.loaded_waypoints: dict[str, "HTTPWaypoint"] = {}
        self.consume_executor = None

    def install(self, application: Application):
        self.application = application
        self.logger.debug(f"Plugin [bold]Microservices[/bold] initialized with default connection: {self.config['default_connection']}")
        
        self.application.app.add_event_handler("startup", self.initialize_connections)
        self.application.app.add_event_handler("shutdown", self.deinitialize_connections)

    def after_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        self.controllers[name] = configuration
        self.active_controllers[name] = instance

    async def initialize_connections(self):
        self.live_connections = await load_backends(self.connections)
        self.application.service_registry.add_singletone(LiveConnections, self.live_connections)
        self.consume_executor = ConsumeExecutor(live_connections=self.live_connections,
                                                default_connection=self.config["default_connection"])
        
        self.loaded_channels = await prepare_channels(self.live_connections, self.controllers)
        await initialize_channels(self.consume_executor, self.loaded_channels)

        if self.use_http_waypoints:
            self.loaded_waypoints = prepare_httpwaypoints(self.controllers)
            initialize_waypoints(self.loaded_waypoints, self.injector)
        
        self.injector.unleash_update()

    async def deinitialize_connections(self):
        for _, live_conneciton in self.live_connections.items():
            await live_conneciton.disconnect()
        
        await disable_waypoint_shared_connectors(self.loaded_waypoints)