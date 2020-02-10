from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.domain.types import DeviceUID


class OperatingSystem(BaseModel):
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int
    install_date: datetime


class User(BaseModel):
    name: str
    domain: str
    fullname: str


class DeviceDetail(BaseModel):
    uid: DeviceUID
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    current_user: Optional[User] = None
    os: List[OperatingSystem]


class DeviceOverview(BaseModel):
    uid: DeviceUID
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    current_user: Optional[User] = None