from __future__ import annotations

from math import nan
from typing import Any

from ..physics_objects.single import is_single
from .n_subjettiness import TauN
from .observable import Observable


class NSubjettinessRatio(Observable):
    def __init__(
        self,
        m: int,
        n: int,
        physics_object: str,
        name: str | None = None,
        value: Any = None,
        dtype: Any = None,
    ):
        supported_types = ["single", "collective"]
        super().__init__(physics_object, supported_types, name, value, dtype)
        self.m = m
        self.n = n

    def read(self, event) -> Any:
        self.physics_object.read(event)

        if is_single(self.physics_object):
            obj = self.physics_object.objects[0]
            tau_m = obj.Tau[self.m - 1] if obj else nan
            tau_n = obj.Tau[self.n - 1] if obj else nan
            self._value = tau_m / tau_n
        else:
            self._value = []
            for obj in self.physics_object.objects:
                if obj is not None:
                    tau_m = obj.Tau[self.m - 1]
                    tau_n = obj.Tau[self.n - 1]
                    self._value.append(tau_m / tau_n)
                else:
                    self._value.append(nan)

        return self

    @property
    def config(self):
        config = super().config
        config.update({"m": self.m, "n": self.n})
        return config


class TauMN(NSubjettinessRatio):
    @property
    def name(self):
        return f"Tau{self.m}{self.n}"

    @classmethod
    def from_identifier(cls, identifier: str, **kwargs) -> TauMN:
        if "." not in identifier:
            raise ValueError(f"Invalid identifier {identifier}.")

        physics_object, name = identifier.split(".")

        m = int(name[-2])
        n = int(name[-1])
        kwargs["m"] = m
        kwargs["n"] = n
        kwargs["physics_object"] = physics_object
        kwargs["name"] = name

        return cls(**kwargs)


NSubjettinessRatio.add_alias("n_subjettiness_ratio")
TauMN.add_alias("tau_mn")
