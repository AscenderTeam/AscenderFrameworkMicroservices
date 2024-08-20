from typing import TYPE_CHECKING
from plugins.microservices.types.http_response import HTTPResponse
from aiohttp import ClientSession, TCPConnector
from contextvars import ContextVar

if TYPE_CHECKING:
    from plugins.microservices.waypoints.registry import WaypointRegistry


class WaypointContext:
    session: ContextVar[ClientSession | None] | ClientSession
    waypoint_registry: "WaypointRegistry"

    def __init__(self, shared_connector: TCPConnector | None, 
                 waypoint_registry: "WaypointRegistry", **session_scope) -> None:
        self.shared_connector = shared_connector
        self.session = ContextVar("session", default=None)
        self.ssl = session_scope["ssl"]
        self.waypoint_registry = waypoint_registry
        del session_scope["ssl"]

        if shared_connector:
            self.session = ClientSession(**session_scope, connector=self.shared_connector)
        
        self._response: ContextVar[HTTPResponse | None] = ContextVar("_response", default=None)
        self._session_scope = session_scope
    
    async def __aenter__(self):
        if self.shared_connector:
            return self.session
        
        session = self.session.get()
        if session is None or session.closed:
            session = ClientSession(**self._session_scope,
                                    connector=TCPConnector(verify_ssl=self.ssl))
            self.session.set(session)

        return session
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.shared_connector:
            return None
        
        session = self.session.get()
        if session and not session.closed:
            await session.close()
            self.session.set(None)

    @property
    def response(self):
        return self._response.get()
    
    @property
    def post(self):
        if self.shared_connector:
            return self.session.post
        
        session = self.session.get()
        return session.post
    
    @property
    def put(self):
        if self.shared_connector:
            return self.session.post
        
        session = self.session.get()
        return session.put
    
    @property
    def patch(self):
        if self.shared_connector:
            return self.session.post
        
        session = self.session.get()
        return session.patch
    
    @property
    def delete(self):
        if self.shared_connector:
            return self.session.post
        
        session = self.session.get()
        return session.delete
    
    @property
    def get(self):
        if self.shared_connector:
            return self.session.post
        
        session = self.session.get()
        return session.get

    def update_response(self, response: HTTPResponse):
        self._response.set(response)