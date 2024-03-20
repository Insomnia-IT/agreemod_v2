from typing import Any, Type

from pydantic import BaseModel

from event_manager.rmq_worker import RMQConfig, RMQConsumer, RMQPublisher

_DOMAIN_EVENT_REGISTRY: dict[str, Type["DomainEvent"]] = {}


def get_event_by_name(name: str) -> Type["DomainEvent"] | None:
    return _DOMAIN_EVENT_REGISTRY.get(name)


class DomainEvent(BaseModel):
    def pack(self) -> dict:
        return {"$event": self.__class__.__name__, "payload": self.model_dump()}

    def __init_subclass__(cls, **kwargs):
        _DOMAIN_EVENT_REGISTRY[cls.__name__] = cls


class BaseConsumer(RMQConsumer):
    __exchange_params__ = RMQConfig.exchange
    __queue_params__ = RMQConfig.queue
    __routing_key__ = "events"

    async def handle_event(self, event: DomainEvent) -> bool: ...

    async def on_message(self, raw_message: dict, headers=None) -> bool:
        if "$event" in raw_message:
            if event_cls := get_event_by_name(raw_message["$event"]):
                event = event_cls.model_validate(raw_message["payload"])
                result = await self.handle_event(event)
                return result
        return False


class BasePublisher(RMQPublisher):
    __exchange_params__ = RMQConfig.exchange
    __routing_key__: str = "events"

    async def send(self, payload: Any, routing_key: str = None, **kwargs):
        message = self.format_message(payload, **kwargs)
        await self.publish(
            message, routing_key=routing_key if routing_key else self.__routing_key__
        )
