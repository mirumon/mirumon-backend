from mirumon.domain.core.dataclass import frozen_dataclass


@frozen_dataclass
class InstalledProgram:
    name: str
    vendor: str
    version: str
