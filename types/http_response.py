from typing import Any
from aiohttp import HttpVersion
from pydantic import BaseModel, ConfigDict


class HTTPResponse(BaseModel):
    model_config: ConfigDict = {"from_attributes": True}
    status: int
    reason: str | None
    version: HttpVersion | None

    content: Any | None