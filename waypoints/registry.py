from contextvars import ContextVar
from typing import Any

from fastapi import Request
from plugins.microservices.types.http_waypoint import HTTPWaypoint


class WaypointRegistry:
    _context: ContextVar[None | Request]
    waypoints: list[HTTPWaypoint]

    def __init__(self) -> None:
        self.identity = False
        self.private_waypoints = False
        
        self.waypoints = []
        self._context = ContextVar("fastapi-request", default=None)
    
    def use_identity(self):
        self.identity = True
    
    def enable_private_waypoints(self):
        self.private_waypoints = True
    
    def add_waypoint(self, _w: HTTPWaypoint):
        if not isinstance(_w, HTTPWaypoint):
            raise TypeError("Waypoint type should be HTTPWaypoint!")
        _w.waypoint_register = self
        self.waypoints.append(_w)
    
    def add_waypoints(self, *_w: HTTPWaypoint):
        for w in _w:
            self.add_waypoint(w)
    
    async def _intercept_middleware(self, request: Request, call_next: Any):
        self._context.set(request)
        
        response = await call_next(request)
        return response
    
    async def _usecontext(self):
        _context = self._context.get()
        self._context.set(None)
        return _context