from typing import TYPE_CHECKING, Callable
from core.application import Application
from core.plugins.plugin import Plugin
from core.types import ControllerModule
from plugins.microservices._core.backend_loader import disable_waypoint_shared_connectors, initialize_channels, initialize_waypoints, load_backends, prepare_channels
from plugins.microservices._core.consume_executor import ConsumeExecutor
from plugins.microservices.redis.engine import RedisEngine
from plugins.microservices.redis.singleton import RedisEngineSingleton
from plugins.microservices.security_manager import SecurityManager
from plugins.microservices.types.channels import ControllerChannel
from plugins.microservices.types.config import MainConfig
from plugins.microservices.types.connections import LiveConnections
from plugins.microservices.waypoints.registry import WaypointRegistry
from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from plugins.microservices.types.http_waypoint import HTTPWaypoint


class AscenderFrameworkMicroservices(Plugin):
    name: str = "ascender-framework-microservices"
    description: str = "Ascender Framework Microservices is the lightweight plugin for Ascender Framework starting from version 1.1.0 that allows Microservice integration using Redis/RabbitMQ/Kafka/TCP Transport"
    
    def __init__(self, config: MainConfig, use_http_waypoints: bool = False, *,
                 waypoint_registry: Callable[[WaypointRegistry], None] = lambda c: None) -> None:
        self.config = config
        self.use_http_waypoints = use_http_waypoints
        self.waypoint_registry = WaypointRegistry()
        self.waypoint_registry_handler = waypoint_registry

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
        self.waypoint_registry_handler(self.waypoint_registry)

        self.application.add_middleware(BaseHTTPMiddleware, dispatch=self.waypoint_registry._intercept_middleware)

    def after_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        self.controllers[name] = configuration
        self.active_controllers[name] = instance

    async def initialize_connections(self):
        # Load security manager
        if internal_policy := self.config.get("internal_privacy", None):
            self.application.service_registry.add_singletone(
                SecurityManager, SecurityManager(internal_policy["current_service_id"],
                                                 internal_policy["secret_key"],
                                                 internal_policy["token_lifetime"],
                                                 internal_policy["allowed_services"]))
        
        # Load backends
        self.live_connections = await load_backends(self.connections)
        self.application.service_registry.add_singletone(LiveConnections, self.live_connections)
        self.consume_executor = ConsumeExecutor(live_connections=self.live_connections,
                                                default_connection=self.config["default_connection"])
        
        self.loaded_channels = await prepare_channels(self.live_connections, self.controllers)
        await initialize_channels(self.consume_executor, self.loaded_channels)

        if self.use_http_waypoints:
            # self.loaded_waypoints = prepare_httpwaypoints(self.controllers)
            initialize_waypoints(self.waypoint_registry.waypoints, self.injector)
        
        RedisEngineSingleton(RedisEngine(self.live_connections))
        self.injector.unleash_update()

    async def deinitialize_connections(self):
        for _, live_conneciton in self.live_connections.items():
            await live_conneciton.disconnect()
        
        await disable_waypoint_shared_connectors(self.loaded_waypoints)