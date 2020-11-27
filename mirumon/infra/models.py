from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel

from mirumon.domain.core.entity import Entity

EntityT = TypeVar("EntityT", bound=Entity)


class InfraModel(Generic[EntityT], BaseModel):
    """Base class for models used in the infrastructure layer."""

    id: Any  # type: ignore
    _entity_type: Type[EntityT]

    @classmethod
    def from_entity(cls, entity: EntityT) -> "InfraModel[EntityT]":
        return cls.parse_obj(entity.dict())

    def to_entity(self) -> EntityT:
        return self._entity_type(**self.dict())

    class Config:
        underscore_attrs_are_private = True
