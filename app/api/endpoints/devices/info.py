from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette import status

from app.api.dependencies.services import get_events_service
from app.domain.device import detail, hardware, software
from app.domain.device.base import DeviceID
from app.domain.device.detail import DeviceDetail, DeviceOverview
from app.domain.event.types import EventTypes
from app.resources import strings
from app.services.devices.events_service import EventsService

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/{0}/{1}".format("{device_id}", event)


@router.get(
    path="",
    name="devices:list",
    description=strings.DEVICES_LIST_DESCRIPTION,
    response_model=List[detail.DeviceOverview],
    # responses=DEVICES_LIST_EXAMPLES,
)
async def devices_list(
    events_service: EventsService = Depends(get_events_service),
) -> List[DeviceOverview]:
    events = []
    for device_id in events_service.gateway.client_ids:
        sync_id = await events_service.send_event_request(
            event_type=EventTypes.list, device_id=device_id, params=[]
        )
        try:
            event = await events_service.listen_event(sync_id)
        except RuntimeError:
            logger.debug(f"timeout on event:{sync_id} for device:{device_id}")
        else:
            events.append(DeviceOverview(online=True, **event.result))

    return events


@router.get(
    path=path(EventTypes.detail),
    name=name(EventTypes.detail),
    description=strings.DEVICE_DETAIL_DESCRIPTION,
    response_model=DeviceDetail,
)
async def get_device_detail(
    device_id: DeviceID, events_service: EventsService = Depends(get_events_service),
) -> DeviceDetail:
    try:
        sync_id = await events_service.send_event_request(
            event_type=EventTypes.detail, device_id=device_id, params=[]
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        event = await events_service.listen_event(sync_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
        )
    return DeviceDetail(online=True, **event.result)


@router.get(
    path=path(EventTypes.hardware),
    name=name(EventTypes.hardware),
    description=strings.DEVICE_HARDWARE_DESCRIPTION,
    response_model=hardware.HardwareModel,
)
async def get_device_hardware(
    # client: app.services.devices.client.DeviceClient = Depends(get_client),
    # events_manager: EventsManager = Depends(events_manager_retriever()),
    # sync_id: SyncID = Depends(get_new_sync_id),
) -> hardware.HardwareModel:
    pass
    # event_payload = EventInRequest(method=EventTypes.hardware, sync_id=sync_id)
    # await client.send_event(event_payload)
    # try:
    #     return await events_manager.wait_event_from_client(
    #         sync_id=event_payload.sync_id, client=client
    #     )
    # except WebSocketDisconnect:
    #     error_detail = (
    #         strings.EVENT_NOT_SUPPORTED
    #         if client.is_connected
    #         else strings.DEVICE_DISCONNECTED
    #     )
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
    #     )


@router.get(
    path=path(EventTypes.software),
    name=name(EventTypes.software),
    description=strings.DEVICE_SOFTWARE_DESCRIPTION,
    response_model=List[software.InstalledProgram],
)
async def get_device_software(
    # client: app.services.devices.client.DeviceClient = Depends(get_client),
    # events_manager: EventsManager = Depends(events_manager_retriever()),
    # sync_id: SyncID = Depends(get_new_sync_id),
) -> software.InstalledProgram:
    pass
    # event_payload = EventInRequest(method=EventTypes.software, sync_id=sync_id)
    # await client.send_event(event_payload)
    # try:
    #     return await events_manager.wait_event_from_client(
    #         sync_id=event_payload.sync_id, client=client
    #     )
    # except WebSocketDisconnect:
    #     error_detail = (
    #         strings.EVENT_NOT_SUPPORTED
    #         if client.is_connected
    #         else strings.DEVICE_DISCONNECTED
    #     )
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
    #     )
