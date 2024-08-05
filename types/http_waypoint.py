from aiohttp.typedefs import LooseCookies, LooseHeaders
from aiohttp import BasicAuth, ClientSession, TCPConnector

from core.registries.service import ServiceRegistry
from plugins.microservices.waypoints.context import WaypointContext
from plugins.microservices.waypoints.instance import WaypointInstance


class HTTPWaypoint:
    def __init__(self, waypoint: type[WaypointInstance], base_url: str,
                 keep_connection: bool = False,
                 cookies: LooseCookies | None = None,
                 headers: LooseHeaders | None = None,
                 ssl: bool = True, auth: BasicAuth | None = None,
                 raise_for_status: bool = False, **additional_configs) -> None:
        self.base_url = base_url
        self.cookies = cookies
        self.headers = headers
        self.keep_connection = keep_connection
        self.ssl = ssl
        self.auth = auth
        self.raise_for_status = raise_for_status
        self.additional_configs = additional_configs

        self.waypoint = waypoint
    
    def define_waypoint(self):
        service_registry = ServiceRegistry()
        
        _context = WaypointContext(TCPConnector(verify_ssl=self.ssl) if self.keep_connection else None, base_url=self.base_url, ssl=self.ssl,
                                cookies=self.cookies, headers=self.headers,
                                auth=self.auth, raise_for_status=self.raise_for_status,
                                **self.additional_configs)
        self._waypoint = self.waypoint(_context)
        
        di_parameters = service_registry.get_parameters(self.waypoint)

        for di_key, di_obj in di_parameters.items():
            setattr(self._waypoint, di_key, di_obj)
        
        service_registry.add_singletone(self.waypoint, self._waypoint)
    
    async def close_waypoint(self):
        if not self.keep_connection:
            return
        print("Closing waypoint", self._waypoint.__class__.__name__)
        await self._waypoint._context.session.close()