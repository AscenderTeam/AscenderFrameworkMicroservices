from logging import Logger
from microservices.typehints.application import Application
from microservices.typehints.types import ControllerModule


class Plugin:
    # Overridable
    name: str
    description: str

    # Shouldn't be overrided
    logger: Logger
    
    # Overridable
    def install(self, application: Application, *args, **kwargs):
        raise NotImplementedError()
    
    def before_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        pass

    def after_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        pass

    def on_dependency_intialization(self, active_controllers: list[object]):
        pass