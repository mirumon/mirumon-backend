from typing import Optional

from pydantic import BaseModel

from app.models.schemas.base import BaseEventResponse, SyncID
from app.models.schemas.events.types import EventParams, EventType, Result, ResultWS


class RegistrationInRequest(BaseModel):
    shared_token: str


class RegistrationInResponse(BaseModel):
    device_token: str


class EventInRequest(BaseModel):
    method: EventType
    event_params: Optional[EventParams] = None
    sync_id: SyncID


class ErrorInResponse(BaseModel):
    code: int
    message: str


class EventInResponse(BaseEventResponse):
    event_result: Optional[Result]
    error: Optional[ErrorInResponse]
    sync_id: SyncID


class EventInRequestWS(BaseModel):
    method: EventType
    event_params: Optional[EventParams] = None


class EventInResponseWS(BaseEventResponse):
    method: EventType
    event_result: Optional[ResultWS]
    error: Optional[ErrorInResponse]
