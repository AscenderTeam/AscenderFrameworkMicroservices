import functools
from typing import Any, Awaitable, Callable, TypeVar
from core.optionals import BaseResponse
from aiohttp import ClientResponse

T = TypeVar("T", bound=BaseResponse)


class WaypointResponse:
    def __init__(self, response_model: type[T], from_json: bool = True) -> None:
        self.response_model = response_model
        self.from_json = from_json
    
    def __call__(self, executable: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(executable)
        async def wrapper(*args, **kwargs) -> T:
            response = await executable(*args, **kwargs)
            if self.from_json:
                return self.response_model.model_validate_json(response)
            
            if isinstance(response, ClientResponse):
                return self.response_model.model_validate_json(await response.json())
            
            return self.response_model.model_validate(response)
        
        return wrapper