import asyncio
import uuid
from typing import Dict, Optional, cast

from loguru import logger
from starlette import websockets

from app.config import REST_MAX_RESPONSE_TIME, REST_SLEEP_TIME
from app.schemas.events.base import Event, EventInResponse, EventPayload, EventType
from app.services.computers import Client


class EventsManager:
    def __init__(self) -> None:
        self._events: Dict[uuid.UUID, Optional[EventInResponse]] = {}
        self._asyncio_events: Dict[uuid.UUID, asyncio.Event] = {}

    def generate_event(self, event_type: EventType) -> Event:
        event_id = uuid.uuid4()
        event = Event(type=event_type, id=event_id)
        self._events[event_id] = EventInResponse(event=event)
        return Event(id=event_id, type=event_type)

    def set_event_response(self, event_id: uuid.UUID, event: EventInResponse) -> None:
        self._events[event_id] = event
        self._asyncio_events[event_id].set()

    # todo create events methods
    async def wait_event_from_client(
        self, event_id: uuid.UUID, client: Client
    ) -> EventPayload:
        event = asyncio.Event()
        self._asyncio_events[event_id] = event
        response_time = REST_MAX_RESPONSE_TIME
        while not event.is_set():
            response_time -= REST_SLEEP_TIME
            try:
                await asyncio.wait_for(event.wait(), REST_SLEEP_TIME)
            except asyncio.futures.TimeoutError:
                if not client.is_connected or not response_time:
                    logger.debug("client disconnected while waiting event")
                    raise websockets.WebSocketDisconnect
        return cast(EventInResponse, self._events.pop(event_id)).payload

    def remove_event(self, event_id: uuid.UUID) -> None:
        self._events.pop(event_id)


async def process_incoming_event(client: Client, manager: EventsManager) -> None:
    response = await client.read_event()
    manager.set_event_response(event_id=response.event.id, event=response)


_events_manager = EventsManager()


def get_events_manager() -> EventsManager:
    return _events_manager