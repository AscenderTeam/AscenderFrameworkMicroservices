from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any, AsyncIterable, Literal, final

from aio_pika import Exchange, Message
from pydantic import BaseModel


from core.optionals.base.dto import BaseDTO
from core.optionals.base.response import BaseResponse
from plugins.microservices.context import CommonContext
from plugins.microservices.context import MessageContext


class Channel:

    exchange: Exchange
    routing_key: str
    
    async def handle(self, ctx: MessageContext):
        pass

    async def success(self, ctx: MessageContext):
        pass

    async def failure(self, ctx: MessageContext, state: Literal["Basic.Nack", "Basic.Reject"]):
        pass
    
    @final
    async def raw_publish(self, body: Any | BaseModel, *, no_cb: bool = False, body_params: dict[str, Any] = {}, routing_key: str = "", mandatory: bool = False, immediate: bool = False, timeout: float | int | None = None):
        _body = body

        if isinstance(_body, (BaseModel, BaseDTO, BaseResponse)):
            _body = body.model_dump_json()

        elif not isinstance(_body, (str, bytes)):
            _body = json.dumps(
                body,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")

        if not isinstance(_body, bytes):
            _body = _body.encode("utf-8")

        delivery = await self.exchange.publish(Message(_body, **body_params), routing_key=routing_key, mandatory=mandatory, immediate=immediate, timeout=timeout)
        common_context = CommonContext(body, _body, delivery.name, routing_key, self.exchange, self, **{
            "mandatory": mandatory,
            "immediate": immediate,
            "timeout": timeout,
        })
        if no_cb:
            return delivery
        
        match delivery.name:
            case "Basic.Ack":
                await self.success(common_context)
            
            case "Basic.Nack":
                await self.failure(common_context, "Basic.Nack")
            
            case "Basic.Reject":
                await self.failure(common_context, "Basic.Reject")
        
        return delivery
    
    @final
    async def astream_publication(self, messages: AsyncIterable[bytes], routing_key: str = "", is_presistant: bool = True):
        if not is_presistant:
            async for message in messages:
                await self.raw_publish(message, routing_key=routing_key, immediate=True)
        
        else:
            async for message in messages:
                await self.raw_publish(message, body_params={"delivery_mode": 2}, routing_key=routing_key, immediate=True)