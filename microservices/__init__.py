from microservices.typehints.application import Application
from microservices.typehints.base import Plugin
from microservices.typehints.types import ControllerModule
from microservices._core.backend_loader import initialize_channels, inject_channels, load_backends, load_stores, prepare_channels
from microservices._core.consume_executor import ConsumeExecutor
from microservices.types.channels import ControllerChannel
from microservices.types.config import MainConfig


class AscenderFrameworkMicroservices(Plugin):
    name: str = "ascender-framework-microservices"
    description: str = "Ascender Framework Microservices is the lightweight plugin for Ascender Framework starting from version 1.1.0 that allows Microservice integration using Redis/RabbitMQ/Kafka/TCP Transport"
    
    def __init__(self, config: MainConfig) -> None:
        self.config = config
        
        self.default_connection = self.config["connections"][self.config["default_connection"]]
        self.connections = self.config["connections"]
        self.controllers: dict[str, ControllerModule] = {}
        self.active_controllers: dict[str, object] = {}
        self.loaded_channels: dict[str, tuple[ControllerChannel, ControllerModule]] = {}
        self.consume_executor = None

    def install(self, application: Application, storage: Distributor):
        self.application = application
        self.distributor = storage
        self.loader = self.application.loader_module
        self.logger.debug(f"Plugin [bold]Microservices[/bold] initialized with default connection: {self.config['default_connection']}")
        
        self.application.app.add_event_handler("startup", self.initialize_connections)
        self.application.app.add_event_handler("shutdown", self.deinitialize_connections)

    
    def after_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        self.controllers[name] = configuration
        self.active_controllers[name] = instance

    async def initialize_connections(self):
        self.live_connections = await load_backends(self.connections)
        self.consume_executor = ConsumeExecutor(live_connections=self.live_connections,
                                                default_connection=self.config["default_connection"])
        
        self.loaded_channels = await prepare_channels(self.live_connections, self.controllers)
        await initialize_channels(self.consume_executor, self.loaded_channels)
        await inject_channels(self.consume_executor, self.active_controllers)

        connection_storage, channel_storages = await load_stores(self.distributor, self.live_connections, self.consume_executor)
        
        self.distributor.register_store("microservice.connections", connection_storage)

        for name, value in channel_storages.items():
            self.distributor.register_store(name, value)

    async def deinitialize_connections(self):
        for _, live_conneciton in self.live_connections.items():
            await live_conneciton.disconnect()