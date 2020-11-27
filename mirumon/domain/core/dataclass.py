from dataclasses import dataclass

frozen_dataclass = dataclass(repr=True, eq=True, frozen=True)
