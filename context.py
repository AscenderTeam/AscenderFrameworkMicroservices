import json
from typing import TYPE_CHECKING, Any, AsyncIterable, Literal
from aio_pika import IncomingMessage, Message, Exchange
from pydantic import BaseModel

if TYPE_CHECKING:
    from plugins.microservices.handler import Channel


class CommonContext:
    def __init__(self, body: Any | BaseModel, body_encoded: bytes,
                 delivery_frame: Literal["Basic.Ack", "Basic.Nack", "Basic.Reject"],
                 routing_key: str, exchanger: Exchange, channel: "Channel", **publication_params) -> None:
        self.body = body
        self.body_encoded = body_encoded
        self.delivery_frame = delivery_frame
        self.routing_key = routing_key
        self.exchanger = exchanger
        self.exchange = self.exchanger.name
        self.channel = channel
    
    async def retry(self, mandatory: bool = False, immediate: bool = False, timeout: float | int | None = None):
        if isinstance(body, BaseModel):
            body = body.model_dump_json()

        if not isinstance(body, (str, bytes)):
            body = json.dumps(
                body,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")

        if not isinstance(body, bytes):
            body = body.encode("utf-8")
        
        return await self.exchanger.publish(Message(self.body_encoded), self.routing_key, mandatory=mandatory, immediate=immediate, timeout=timeout)


class MessageContext:
    def __init__(self, message: IncomingMessage, exchanger: Exchange, channel: "Channel") -> None:
        self.message = message
        self.exchanger = exchanger
        self.__channel = channel
    
    @property
    def ack(self):
        return self.message.ack
    
    @property
    def nack(self):
        return self.message.nack
    
    @property
    def reject(self):
        return self.message.reject
    
    async def raw_publish(self, body: Any | BaseModel, *, exchange: str = "", routing_key: str = "", properties: Any | None = None, mandatory: bool = False, immediate: bool = False, timeout: float | int | None = None):
        if isinstance(body, BaseModel):
            body = body.model_dump_json()

        if not isinstance(body, (str, bytes)):
            body = json.dumps(
                body,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")

        if not isinstance(body, bytes):
            body = body.encode("utf-8")

        delivery = await self.message.channel.basic_publish(body, exchange=exchange, routing_key=routing_key, properties=properties, mandatory=mandatory, immediate=immediate, timeout=timeout)
        
        match delivery.name:
            case "Basic.Ack":
                await self.__channel.success(self)
            
            case "Basic.Nack":
                await self.__channel.failure(self, "Basic.Nack")
            
            case "Basic.Reject":
                await self.__channel.failure(self, "Basic.Reject")
        
        return delivery
    
    async def respond_direct(self, body: Any | BaseModel, routing_key: str = "", immediate: bool = False, timeout: float | int | None = None):
        if isinstance(body, BaseModel):
            body = body.model_dump_json()

        if not isinstance(body, (str, bytes)):
            body = json.dumps(
                body,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")

        if not isinstance(body, bytes):
            body = body.encode("utf-8")
            
        delivery = await self.message.channel.basic_publish(body, exchange=self.message.exchange, routing_key=routing_key, immediate=immediate, timeout=timeout)
        match delivery.name:
            case "Basic.Ack":
                await self.__channel.success(self)
            
            case "Basic.Nack":
                await self.__channel.failure(self, "Basic.Nack")
            
            case "Basic.Reject":
                await self.__channel.failure(self, "Basic.Reject")

    async def astream_publication_back(self, messages: AsyncIterable[bytes], routing_key: str = "", is_presistant: bool = True):
        exchange = self.exchanger

        if not is_presistant:
            async for message in messages:
                await self.raw_publish(message, exchange=exchange.name, routing_key=routing_key, immediate=True)
        
        else:
            async for message in messages:
                await self.exchanger.publish(Message(message, delivery_mode=2), routing_key=routing_key, immediate=True)