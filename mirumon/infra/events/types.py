from mirumon.domain.core.enums import StrEnum


class EventTypes(StrEnum):
    # system events
    error: str = "error"

    # device events
    detail: str = "detail"
    hardware: str = "hardware"
    software: str = "software"

    execute: str = "execute"
    shutdown: str = "shutdown"

    def __str__(self) -> str:
        return self.value


class StatusTypes(StrEnum):
    ok = "ok"
    error = "error"