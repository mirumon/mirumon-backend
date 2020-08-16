from json import JSONDecodeError

from fastapi import APIRouter, Depends, Header
from loguru import logger
from pydantic import ValidationError
from starlette import status, websockets
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.dependencies.connections import get_clients_gateway
from app.api.dependencies.services import get_devices_auth_service, get_events_service
from app.services.devices.auth_service import DevicesAuthService
from app.services.devices.client import DeviceClient
from app.services.devices.events_service import EventsService
from app.services.devices.gateway import DeviceClientsGateway

router = APIRouter()


async def get_registered_device_client(
    websocket: WebSocket,
    token: str = Header(None),
    auth_service: DevicesAuthService = Depends(get_devices_auth_service),
    clients_manager: DeviceClientsGateway = Depends(get_clients_gateway),
) -> DeviceClient:
    await websocket.accept()
    try:
        device = await auth_service.get_device_from_token(token)
    except RuntimeError:
        logger.debug("device token decode error")
        await websocket.close(status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect
    else:
        client = DeviceClient(device_id=device.id, websocket=websocket)
        clients_manager.add_client(client)
        return client


@router.websocket("/service", name="devices:service")
async def device_ws_endpoint(
    client: DeviceClient = Depends(get_registered_device_client),
    events_service: EventsService = Depends(get_events_service),
    clients_manager: DeviceClientsGateway = Depends(get_clients_gateway),
) -> None:
    while client.is_connected:
        try:
            event = await client.read_event()
        except (ValidationError, JSONDecodeError) as validation_error:
            logger.debug("error {0}", validation_error)
            await client.send_error(str(validation_error))
        except websockets.WebSocketDisconnect as disconnect_error:
            logger.info(
                "device:{0} disconnected, reason {1}",
                client.device_id,
                disconnect_error,
            )
            clients_manager.remove_client(client)
        else:
            logger.debug("received event from device")
            await events_service.send_event_response(event)
