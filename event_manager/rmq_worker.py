import asyncio
import json

from asyncio import Task
from datetime import datetime, timedelta
from logging import getLogger
from typing import Any

import aiormq
import pydantic

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection


_logger = getLogger(__name__)


class RMQConfig:
    # queue
    # qos = dict(prefetch_count=2)
    queue = dict(
        durable=True,
        auto_delete=False,
    )

    # exchange
    exchange = dict(
        durable=True,
        auto_delete=False,
        type=ExchangeType.FANOUT,
    )


class RMQWorker:
    started: bool = False
    should_exit: bool = False

    connection_task: Task | None
    connection: AbstractRobustConnection | None = None

    def __init__(self, connect_url: str) -> None:
        self.connect_url = connect_url

    async def _connect(self):
        self.connection = await connect_robust(self.connect_url)

    async def connect(self):
        while not self.should_exit:
            try:
                await self._connect()
                break
            except aiormq.exceptions.AMQPConnectionError as e:
                _cooldown = 3
                _logger.warning("Connection error: %s", e)
                _logger.info("Trying again in %s seconds", _cooldown)
                await asyncio.sleep(_cooldown)

    async def start(self):
        _logger.info("Starting worker: %s", type(self).__name__)
        self.connection_task = asyncio.create_task(self.connect())

    async def stop(self):
        _logger.info("Stopping worker: %s", type(self).__name__)

        self.should_exit = True

        if not self.connection_task.done():
            self.connection_task.cancel()
        elif self.connection and self.connection.connected.is_set():
            _logger.info("Closing RMQ connection")
            await self.connection.close()


class RMQConsumer(RMQWorker):
    __queue__: str = None
    __queue_params__: dict = {}
    __exchange__: str = None
    __exchange_params__: dict = {}
    __routing_key__: str = None

    def __init__(self, connect_url: str) -> None:
        super().__init__(connect_url)

    async def on_message(self, message: dict, headers=None) -> bool:
        ...

    async def _on_message(self, message: AbstractIncomingMessage):
        try:
            _logger.info(
                "Message received: body='%s' headers='%s'",
                message.body.decode(),
                message.headers,
            )
            payload = json.loads(message.body.decode())
            headers = message.headers
            result = await self.on_message(payload, headers)
            if result:
                await message.ack()
            else:
                await message.reject()
                _logger.error(
                    "Message is not processed: body='%s', headers='%s'",
                    message.body.decode(),
                    message.headers,
                )
        except json.JSONDecodeError:
            await message.reject()
            _logger.error("Invalid JSON: '%s'", message.body.decode())
        except Exception as e:
            await message.reject()
            _logger.error(
                "Message processing failed with exception. '%s: %s'",
                e.__class__.__name__,
                e,
            )

    async def _connect(self):
        await super()._connect()

        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=2)
        queue = await channel.declare_queue(self.__queue__, **self.__queue_params__)
        _logger.info(
            "Queue declared: '%s', auto_delete = '%s', durable = '%s'",
            queue.name,
            queue.auto_delete,
            queue.durable,
        )
        exchange = await channel.declare_exchange(self.__exchange__, **self.__exchange_params__)
        _logger.info(
            "Exchange declared: '%s', " "type = '%s', " "auto_delete = '%s', " "durable = '%s', " "bindings = '%s'",
            exchange.name,
            exchange.__dict__["_type"],
            exchange.__dict__["auto_delete"],
            exchange.__dict__["auto_delete"],
            exchange.__dict__["_bindings"],
        )
        await queue.bind(exchange=exchange, routing_key=self.__routing_key__)
        _logger.info(
            "Queue '%s' binded to exchange '%s' on routing_key '%s'",
            queue.name,
            exchange.name,
            self.__routing_key__,
        )
        _logger.info("Start consuming")
        self.queue = queue

        await queue.consume(self._on_message)


class RMQPublisher(RMQWorker):
    __exchange__: str = None
    __exchange_params__: dict = {}

    def __init__(self, connect_url: str) -> None:
        super().__init__(connect_url)

    def format_message(
        self,
        payload: Any,
        headers: dict = None,
        content_type: str = None,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
        priority: int = None,
        correlation_id: str = None,
        reply_to: str = None,
        expiration: datetime | timedelta = None,
        message_id: str = None,
        timestamp: int | datetime = None,
    ) -> Message:
        match payload:
            case str():
                message = payload.encode()
            case dict() | list():
                message = json.dumps(payload).encode()
            case pydantic.BaseModel():
                message = payload.model_dump_json().encode()
            case _:
                message = bytes()
        return Message(
            body=message,
            headers=headers,
            content_type=content_type,
            delivery_mode=delivery_mode,
            priority=priority,
            correlation_id=correlation_id,
            reply_to=reply_to,
            expiration=expiration,
            message_id=message_id,
            timestamp=timestamp,
        )

    async def publish(self, message: Message, routing_key: str = None):
        _logger.info(
            "Publishing message: body='%s', headers='%s' on exchange '%s' with routing_key '%s'",
            message.body.decode(),
            message.headers,
            self.exchange.name,
            routing_key,
        )
        await self.exchange.publish(message, routing_key=routing_key)

    async def _connect(self):
        await super()._connect()
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(self.__exchange__, **self.__exchange_params__)
        _logger.info(
            "Exchange declared: '%s', " "type = '%s', " "auto_delete = '%s', " "durable = '%s', " "bindings = '%s'",
            self.exchange.name,
            self.exchange.__dict__["_type"],
            self.exchange.__dict__["auto_delete"],
            self.exchange.__dict__["durable"],
            self.exchange.__dict__["_bindings"],
        )

    async def stop(self):
        await self.connection.close()
