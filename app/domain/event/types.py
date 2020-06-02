from enum import Enum


class EventTypes(str, Enum):  # noqa: WPS600
    list: str = "list"

    detail: str = "detail"
    hardware: str = "hardware"
    software: str = "software"

    execute: str = "execute"
    shutdown: str = "shutdown"

    def __str__(self) -> str:
        return self.value
