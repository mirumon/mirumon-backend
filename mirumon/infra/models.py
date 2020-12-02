from typing import Any, Generic, Type, TypeVar, ClassVar, get_args

from pydantic import BaseModel

from mirumon.domain.core.entity import Entity

EntityT = TypeVar("EntityT", bound=Entity)


class InfraModel(Generic[EntityT], BaseModel):  # type: ignore
    """Base class for models used in the infrastructure layer."""

    id: Any  # type: ignore

    @classmethod
    def from_entity(cls, entity: EntityT) -> "InfraModel[EntityT]":
        return cls.parse_obj(entity.dict())

    def to_entity(self) -> EntityT:
        entity: EntityT = get_args(InfraModel[EntityT])[0]
        return entity(**self.dict())  # type: ignore

    class Config:
        underscore_attrs_are_private = True
