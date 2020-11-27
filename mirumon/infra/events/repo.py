from asyncio import exceptions
from typing import Optional

from aio_pika import Exchange, Message, Queue
from aio_pika.queue import QueueIterator
from async_timeout import timeout
from loguru import logger
from pydantic import ValidationError

from mirumon.infra.components.rabbitmq.repo import RabbitMQRepository
from mirumon.infra.events.events import EventID, EventInResponse, EventResult
from mirumon.infra.events.types import EventTypes


class EventProcessError(Exception):
    """Error class for exit from consuming event."""


class EventsRepository(RabbitMQRepository):
    def __init__(
        self, queue: Queue, exchange: Exchange, process_timeout: float
    ) -> None:
        self.queue: Queue = queue
        self.exchange: Exchange = exchange
        self.process_timeout = process_timeout

    async def publish_event_response(self, event: EventInResponse) -> None:
        body = event.json().encode()
        message = Message(body)
        logger.debug(f"publish event response message:{message}\nwith body:{body}")
        await self.exchange.publish(message, routing_key="info")

    async def process_event(
        self,
        event_id: EventID,
        event_type: EventTypes,
        *,
        process_timeout: Optional[float] = None,
    ) -> EventResult:
        logger.debug("start processing event:{0}", event_id)
        process_timeout = process_timeout or self.process_timeout
        print(process_timeout)
        try:
            async with timeout(timeout=process_timeout):
                return await self._wait_event(event_id, event_type)
        except exceptions.TimeoutError:
            raise EventProcessError(f"timeout error on event:{event_id}")
        except RuntimeError:
            raise EventProcessError(
                f"response with error from device on event:{event_id}"
            )

    async def _wait_event(
        self, event_id: EventID, event_type: EventTypes
    ) -> EventResult:
        async with self.queue.iterator() as queue_iter:
            return await _process_message(queue_iter, event_id, event_type)


async def _process_message(  # noqa: WPS231
    queue_iter: QueueIterator, event_id: EventID, event_type: EventTypes
) -> EventResult:
    async for message in queue_iter:
        async with message.process():
            try:
                event = _validate_incoming_event(message)
            except ValidationError as error:
                logger.error(f"event message validation error:{error.errors()}")
                continue

            if event.id != event_id:
                continue

            if event.is_success and event.method == event_type:
                return event.result
            raise RuntimeError("event contains error")
    raise RuntimeError("Something gone really bad..")


def _validate_incoming_event(message: Message) -> EventInResponse:
    raw_payload = message.body.decode()
    logger.debug(f"process message: {raw_payload}")
    return EventInResponse.parse_raw(raw_payload)
