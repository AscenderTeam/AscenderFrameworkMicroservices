import functools
from json import JSONDecodeError
import re
from warnings import warn
from aiohttp import ClientResponse, ClientSession
from pydantic import validate_call
from typing import Any, Awaitable, Callable, Literal, TypeVar

from core.optionals import BaseDTO, BaseResponse
from plugins.microservices.types.http_response import HTTPResponse


T = TypeVar("T", bound=BaseResponse)
C = TypeVar("C")
D = TypeVar("D")


class WaypointBranch:
    def __init__(self, path: str, 
                 method: Literal["get", "post", "put", "patch", "delete"],
                 *,
                 serialize_model: type[T] | None = None) -> None:
        self.path = path
        self.method = method
        self.path_params = re.findall(r"\{(\w+)\}", self.path)
        self.serialize_model = serialize_model

    def prepare_request(self, callback: Callable[..., Awaitable[Any]], *args, **kwargs):
        path_parameters = {}
        query_parameters = {}
        body = None
        
        for _name, _val in kwargs.items():
            if _name in self.path_params:
                path_parameters[_name] = _val
                continue
            
            if isinstance(_val, BaseDTO) and self.method not in ["get", "delete"]:
                body = _val.model_dump_json()
                continue

            query_parameters[_name] = _val
        return {"paths": path_parameters, 
                "queries": query_parameters, 
                "body": body}

    def format_path(self, path_params: dict[str, Any]):
        self.path = self.path.format(**path_params)

    async def invoke_request(self, callback: Callable[..., Awaitable[Any]], *args, **kwargs):
        request_data = self.prepare_request(callback, *args, **kwargs)
        self.format_path(request_data["paths"])

        async with args[0]._context as session:
            async with getattr(session, self.method)(self.path, params=request_data["queries"],
                                                        json=request_data["body"]) as _response:
                await args[0].update_response(_response)
                _response.close()
            
            if self.serialize_model:
                response = await callback(*args, **kwargs)
                if isinstance(response, ClientResponse):
                    return self.serialize_model.model_validate_json(await response.json()) 
                
                return self.serialize_model.model_validate_json(response)
        
        return await callback(*args, **kwargs)

    def __call__(self, executable: Callable[[C], Awaitable[D]]):
        executable = validate_call(executable)

        @functools.wraps(executable)
        async def wrapper(*args, **kwargs) -> T | D:
            return await self.invoke_request(executable, *args, **kwargs)
        
        return wrapper