from typing import Any, Callable


class Application:
    def __init__(self, 
                controllers: list[Any] = [],
                on_server_start: Callable[['Application'], None] | None = None, 
                on_server_runtime_error: Callable[[Exception], None] | None = None,
                on_cli_run: Callable[['Application', Any], None] | None = None,
                on_injections_run: Callable[['Application'], None] | None = None,
                on_event_start: Callable[['Application', list[object]], None] = None,
                on_event_shutdown: Callable[['Application', list[object]], None] = None) -> None:

        self._on_server_start = on_server_start
        self._on_server_runtime_error = on_server_runtime_error
        self._on_cli_run = on_cli_run
        self._on_injections_run = on_injections_run
        self._on_event_start = on_event_start
        self._on_event_shutdown = on_event_shutdown