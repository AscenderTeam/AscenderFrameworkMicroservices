from typing import TypeVar, TypedDict

S = TypeVar(name="S")
R = TypeVar(name="R")
E = TypeVar(name="E")

class ControllerModule(TypedDict):
    name: str | None
    controller: object
    services: dict[str, type[S]]
    repository: type[R] | None
    repository_entities: dict[str, E]
    plugin_configs: dict[str, any]