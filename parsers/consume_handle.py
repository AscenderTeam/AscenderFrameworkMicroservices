import inspect
from typing import Any, Awaitable, Callable

from core.optionals.base.dto import BaseDTO


class ConsumeHandleParser:
    def __init__(self, handle_method: Callable[..., Awaitable[None]]) -> None:
        self.handle_method = handle_method
    
    def get_parameters(self):
        obj_args = inspect.signature(self.handle_method).parameters
        
        body: BaseDTO | None = None
        for name, abstract in obj_args.items():
            # abstract: inspect.Parameter = abstract
            abstract = abstract.annotation
            if name in ["body", "dto", "content"]:
                body = abstract
        return body

    def __call__(self, data: Any) -> Any:
        _body = self.get_parameters()
        if not _body:
            return None
        
        return _body.model_validate_json(data)