from mirumon.infra.api.models.base import APIModel


class InstalledProgram(APIModel):
    name: str
    vendor: str
    version: str