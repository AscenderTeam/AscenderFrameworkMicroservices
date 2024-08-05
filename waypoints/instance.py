from json import JSONDecodeError
from typing import TYPE_CHECKING
from plugins.microservices.types.http_response import HTTPResponse
from plugins.microservices.waypoints.context import WaypointContext

if TYPE_CHECKING:
    from aiohttp import ClientResponse


class WaypointInstance:
    def __init__(self, _context: WaypointContext) -> None:
        self._context = _context
        self._response = self._context.response
    
    async def update_response(self, response: "ClientResponse"):
        try:
            return self._context.update_response(HTTPResponse(status=response.status,
                                                          reason=response.reason,
                                                          version=response.version,
                                                          content=await response.json()))
        except JSONDecodeError:
            return self._context.update_response(HTTPResponse(status=response.status,
                                                          reason=response.reason,
                                                          version=response.version,
                                                          content=None))
                                                          