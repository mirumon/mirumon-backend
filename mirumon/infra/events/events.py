from typing import Any, Dict, Generic, NewType, Optional, TypeVar, Union
from uuid import UUID

from pydantic import validator

from mirumon.domain.events import device_detail, device_hardware, device_software
from mirumon.infra.api.models.base import APIModel
from mirumon.infra.events.types import EventTypes, StatusTypes

EventID = NewType("EventID", UUID)
EventParams = NewType("EventParams", dict)  # type: ignore

EventResultT = TypeVar("EventResultT", bound=APIModel)


class EventError(APIModel):
    code: int
    detail: Union[list, dict, str]  # type: ignore


class EventInRequest(APIModel):
    id: EventID
    method: EventTypes
    params: Optional[EventParams] = None


class EventInResponse(Generic[EventResultT], APIModel):
    status: StatusTypes
    id: EventID
    method: EventTypes
    result: Optional[EventResultT]
    error: Optional[EventError]

    @property
    def is_success(self) -> bool:
        return self.status == StatusTypes.ok and self.result is not None

    @property
    def payload(self) -> EventResultT:
        if not self.is_success:
            raise RuntimeError("event contains error")
        return self.result  # type: ignore

    @classmethod
    @validator("error", always=True)
    def check_event_or_error(  # type:ignore
        cls,
        value: Any,
        values: dict,  # type: ignore
    ) -> Optional[EventError]:
        # todo: add check pairs ok:result, error:error
        if value is not None and values["result"] is not None:
            raise ValueError("must not provide both result and error")
        if value is None and values.get("result") is None:
            raise ValueError("must provide result or error")
        return value

    @classmethod
    @validator("result")
    def check_event_type_and_payload(
        cls, value: Optional[dict], values: Dict[str, Any]
    ) -> Optional[EventResultT]:
        if value is None:
            return value

        mapper = {
            EventTypes.detail: device_detail.DeviceDetail,
            EventTypes.hardware: device_hardware.HardwareInfraModel,
            EventTypes.software: device_software.InstalledProgram,
            EventTypes.execute: dict,
            EventTypes.shutdown: dict,
        }
        model = mapper.get(values["method"])
        if not model:
            raise ValueError(f"not found model for event of type {value}")
