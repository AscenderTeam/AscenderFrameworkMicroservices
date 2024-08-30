from logging import getLogger
from time import time
from typing import TYPE_CHECKING, Unpack
from plugins.microservices.types.http_response import HTTPResponse
from aiohttp import ClientResponse, ClientSession, TCPConnector
from aiohttp.typedefs import StrOrURL
from aiohttp.client import _RequestOptions
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
        self.logger = getLogger("ascender-plugins")
    
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
    
    async def post(
        self, 
        url: StrOrURL,
        **kwargs: Unpack[_RequestOptions]
    ):      
        # Defining request start time
        start_time = time()

        # Executing wrapped function
        _response = await self._execute_request("post", url, **kwargs)
        _response_body = await _response.json()

        # Defining response time
        response_time = time()

        # Caluclating time
        request_time = response_time - start_time
        
        self.logger.info(
            f"[cyan] [bold]POST[/bold] request to: {_response.url} with " \
            f"[yellow] SSL {'[green]enabled[/green]' if self.ssl else '[red]disabled[/red]'} [yellow] [/cyan] " \
            f"| Time: {request_time}s | Response Status: {_response.status}"
        )
        
        self.logger.debug(
            "[blue] HTTP transaction details: [/blue]" \
            f"[cyan] Request: [bold]POST[/bold] {_response.url} [/cyan] " \
            f"[green] Headers: {kwargs['headers']} | Body: {kwargs['json'] or kwargs['data']} [/green] " \
            f"[yellow] Response: Status [bold]{_response.status}[/bold] | Headers: {_response.headers} | Body: {_response_body} [/yellow]" \
        )
        return HTTPResponse(status=_response.status, 
                            reason=_response.reason,
                            version=_response.version,
                            content=_response_body)
    
    async def put(
        self, 
        url: StrOrURL,
        **kwargs: Unpack[_RequestOptions]
    ):    
        # Defining request start time
        start_time = time()

        # Executing wrapped function
        _response = await self._execute_request("put", url, **kwargs)
        _response_body = await _response.json()

        # Defining response time
        response_time = time()

        # Caluclating time
        request_time = response_time - start_time
        
        self.logger.info(
            f"[cyan] [bold]PUT[/bold] request to: {_response.url} with " \
            f"[yellow] SSL {'[green]enabled[/green]' if self.ssl else '[red]disabled[/red]'} [yellow] [/cyan] " \
            f"| Time: {request_time}s | Response Status: {_response.status}"
        )
        
        self.logger.debug(
            "[blue] HTTP transaction details: [/blue]" \
            f"[cyan] Request: [bold]PUT[/bold] {_response.url} [/cyan] " \
            f"[green] Headers: {kwargs['headers']} | Body: {kwargs['json'] or kwargs['data']} [/green] " \
            f"[yellow] Response: Status [bold]{_response.status}[/bold] | Headers: {_response.headers} | Body: {_response_body} [/yellow]" \
        )
        return HTTPResponse(status=_response.status, 
                            reason=_response_body,
                            version=_response.version,
                            content=_response_body)
    
    async def patch(
        self, 
        url: StrOrURL,
        **kwargs: Unpack[_RequestOptions]
    ):
        # Defining request start time
        start_time = time()

        # Executing wrapped function
        _response = await self._execute_request("patch", url, **kwargs)
        _response_body = await _response.json()

        # Defining response time
        response_time = time()

        # Caluclating time
        request_time = response_time - start_time
        
        self.logger.info(
            f"[cyan] [bold]PATCH[/bold] request to: {_response.url} with " \
            f"[yellow] SSL {'[green]enabled[/green]' if self.ssl else '[red]disabled[/red]'} [yellow] [/cyan] " \
            f"| Time: {request_time}s | Response Status: {_response.status}"
        )
        
        self.logger.debug(
            "[blue] HTTP transaction details: [/blue]" \
            f"[cyan] Request: [bold]PATCH[/bold] {_response.url} [/cyan] " \
            f"[green] Headers: {kwargs['headers']} | Body: {kwargs['json'] or kwargs['data']} [/green] " \
            f"[yellow] Response: Status [bold]{_response.status}[/bold] | Headers: {_response.headers} | Body: {_response_body} [/yellow]" \
        )
        return HTTPResponse(status=_response.status, 
                            reason=_response_body,
                            version=_response.version,
                            content=_response_body)
    
    async def delete(
        self, 
        url: StrOrURL,
        **kwargs: Unpack[_RequestOptions]
    ):
        # Defining request start time
        start_time = time()

        # Executing wrapped function
        _response = await self._execute_request("delete", url, **kwargs)
        _response_body = await _response.json()

        # Defining response time
        response_time = time()

        # Caluclating time
        request_time = response_time - start_time
        
        self.logger.info(
            f"[cyan] [bold]DELETE[/bold] request to: {_response.url} with " \
            f"[yellow] SSL {'[green]enabled[/green]' if self.ssl else '[red]disabled[/red]'} [yellow] [/cyan] " \
            f"| Time: {request_time}s | Response Status: {_response.status}"
        )
        
        self.logger.debug(
            "[blue] HTTP transaction details: [/blue]" \
            f"[cyan] Request: [bold]DELETE[/bold] {_response.url} [/cyan] " \
            f"[green] Headers: {kwargs['headers']} | Body: {kwargs['json'] or kwargs['data']} [/green] " \
            f"[yellow] Response: Status [bold]{_response.status}[/bold] | Headers: {_response.headers} | Body: {_response_body} [/yellow]" \
        )
        return HTTPResponse(status=_response.status, 
                            reason=_response_body,
                            version=_response.version,
                            content=_response_body)
    
    async def get(
        self, 
        url: StrOrURL,
        **kwargs: Unpack[_RequestOptions]
    ):
        # Defining request start time
        start_time = time()

        # Executing wrapped function
        _response = await self._execute_request("get", url, **kwargs)
        _response_body = await _response.json()

        # Defining response time
        response_time = time()

        # Caluclating time
        request_time = response_time - start_time
        
        self.logger.info(
            f"[cyan] [bold]GET[/bold] request to: {_response.url} with " \
            f"[yellow] SSL {'[green]enabled[/green]' if self.ssl else '[red]disabled[/red]'} [yellow] [/cyan] " \
            f"| Time: {request_time}s | Response Status: {_response.status}"
        )
        
        self.logger.debug(
            "[blue] HTTP transaction details: [/blue]" \
            f"[cyan] Request: [bold]GET[/bold] {_response.url} [/cyan] " \
            f"[green] Headers: {kwargs['headers']} [/green] " \
            f"[yellow] Response: Status [bold]{_response.status}[/bold] | Headers: {_response.headers} | Body: {_response_body} [/yellow]" \
        )
        return HTTPResponse(status=_response.status, 
                            reason=_response_body,
                            version=_response.version,
                            content=_response_body)

    async def _execute_request(
        self,
        method: str,
        url: StrOrURL,
        **kwargs: Unpack[_RequestOptions]
    ) -> ClientResponse:
        """
        NOTE: This is an internal method and is prohibited to use outside of `WaypointContext` object's scope
        """
        # NOTE: If shared connector, where `keep_connection=True`
        if self.shared_connector:
            _response = await getattr(self.session, method)(url, **kwargs)
        
        else:
            session = self.session.get()
            _response = await getattr(session, method)(url, **kwargs)

        return _response

    def update_response(self, response: HTTPResponse):
        self._response.set(response)