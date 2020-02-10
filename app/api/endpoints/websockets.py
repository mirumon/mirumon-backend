from json import JSONDecodeError

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies.managers import (
    clients_manager_retriever,
    events_manager_retriever,
)
from app.api.dependencies.websockets import get_new_client
from app.models.schemas.events.rest import ErrorInResponse
from app.models.schemas.events.ws import EventInRequestWS, EventInResponseWS
from app.services.clients_manager import ClientsManager, DeviceClient
from app.services.devices import get_devices_list
from app.services.events_manager import EventsManager

router = APIRouter()

WS_BAD_REQUEST = 400  # fixme change to correct code
WS_NOT_FOUND = 404
SERVER_ERROR = 500


@router.websocket("/service", name="ws:service")
async def clients_websocket_endpoint(
    events_manager: EventsManager = Depends(
        events_manager_retriever(for_websocket=True)
    ),
    client: DeviceClient = Depends(get_new_client),
    manager: ClientsManager = Depends(clients_manager_retriever(for_websocket=True)),
) -> None:
    manager.add_client(client)
    while True:
        try:
            event_response = await client.read_event()
            events_manager.set_event_response(
                sync_id=event_response.sync_id, event_response=event_response
            )
        except (ValidationError, JSONDecodeError) as error:
            await client.send_error(error, WS_BAD_REQUEST)
        except websockets.WebSocketDisconnect:
            logger.error(f"client with id {client.device_uid} disconnected")
            manager.remove_client(client)
            break
        except Exception as undefined_error:
            await client.send_error(undefined_error, SERVER_ERROR)
            logger.exception(undefined_error)


@router.websocket("/clients", name="ws:clients")
async def api_websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(
        clients_manager_retriever(for_websocket=True)
    ),
    events_manager: EventsManager = Depends(
        events_manager_retriever(for_websocket=True)
    ),
) -> None:
    await websocket.accept()
    while True:
        try:
            payload = await websocket.receive_json()
            event = EventInRequestWS(**payload)
            event_payload = await get_devices_list(clients_manager, events_manager)
            event_response = EventInResponseWS(
                method=event.method, result=event_payload
            )
            logger.debug(event_response)
            await websocket.send_text(event_response.json())
        except ValidationError as validation_error:
            await websocket.send_text(validation_error.json())
            continue
        except KeyError:  # todo add value error
            await websocket.send_json(
                EventInResponseWS(
                    method=event.method,
                    error=ErrorInResponse(
                        code=WS_NOT_FOUND, message="device not found"
                    ),
                )
            )
        except WebSocketDisconnect:
            logger.info(
                "{0} websocket api client {1} [closed]".format(
                    websocket.scope.get("client", ""),
                    websocket.scope.get("raw_path", ""),
                )
            )
            break