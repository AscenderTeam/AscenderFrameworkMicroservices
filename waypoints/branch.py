import functools
from json import JSONDecodeError
import json
import re
from warnings import warn
from aiohttp import ClientResponse, ClientSession
from fastapi import Request
from pydantic import validate_call
from typing import Any, Awaitable, Callable, Literal, TypeVar

from core.optionals import BaseDTO, BaseResponse
from plugins.microservices.types.http_response import HTTPResponse
from plugins.microservices.waypoints.context import WaypointContext


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
        header_parameters = None
        body = None
        
        for _name, _val in kwargs.items():
            if _name in self.path_params:
                path_parameters[_name] = _val
                continue
            
            if _name == "headers":
                header_parameters = _val
                continue

            if isinstance(_val, BaseDTO) and self.method not in ["get", "delete"]:
                body = _val.model_dump_json()
                body = json.loads(body)
                continue

            query_parameters[_name] = _val
        return {"paths": path_parameters, 
                "queries": query_parameters, 
                "headers": header_parameters,
                "body": body}

    def format_path(self, path_params: dict[str, Any]):
        self.path = self.path.format(**path_params)
    
    async def prepare_headers(self, headers: dict[str, Any] | None,
                        context: WaypointContext):
        if context.waypoint_registry.identity:
            if request := await context.waypoint_registry._usecontext():
                if not (auth_headers := request.headers.get("Authorization", None)):
                    return headers
            
                if not headers:
                    return {"Authorization": auth_headers}
                return {**headers, "Authorization": auth_headers}
            
            return headers
        
        if not headers:
            return None
        
        return headers

    async def invoke_request(self, callback: Callable[..., Awaitable[Any]], *args, **kwargs):
        request_data = self.prepare_request(callback, *args, **kwargs)
        headers = await self.prepare_headers(request_data["headers"], args[0]._context)
        self.format_path(request_data["paths"])

        async with args[0]._context as session:
            async with getattr(session, self.method)(self.path, params=request_data["queries"],
                                                        json=request_data["body"], headers=headers) as _response:
                await args[0].update_response(_response)
                _response.close()
            
            if self.serialize_model:
                response = await callback(*args, **kwargs)
                if isinstance(response, HTTPResponse):
                    return self.serialize_model.model_validate(response.content)
                
                if isinstance(response, str):
                    return self.serialize_model.model_validate_json(response)
                
                return self.serialize_model.model_validate(response)
        
        return await callback(*args, **kwargs)

    def __call__(self, executable: Callable[[C], Awaitable[D]]):
        executable = validate_call(executable)

        @functools.wraps(executable)
        async def wrapper(*args, **kwargs) -> T | D:
            return await self.invoke_request(executable, *args, **kwargs)
        
        return wrapper