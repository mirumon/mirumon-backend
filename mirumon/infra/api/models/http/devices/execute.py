from typing import List

from mirumon.infra.api.models.base import APIModel


class ExecuteCommandParams(APIModel):
    command: str
    args: List[str]
