from typing import Self

import awkward as ak
import numpy as np
from typeguard import typechecked

from ..events import Events
from ..physics_objects import PhysicsObject
from ..saving import registered_object
from ..types import AwkwardArray
from .azimuthal_angle import Phi
from .observable import Observable
from .pseudo_rapidity import Eta


@typechecked
@registered_object(r"(?P<physics_object>[\w:._,]+)\.(DeltaR|delta_r)")
class DeltaR(Observable):
    def __init__(self, physics_object: list[str | PhysicsObject], **kwargs) -> None:
        super().__init__(physics_object, **kwargs)

        if len(physics_object) != 2:
            raise ValueError("DeltaR requires exactly two physics objects.")

    def get_array(self, events: Events) -> AwkwardArray:
        eta0 = Eta(self.physics_object[0]).read(events).array
        phi0 = Phi(self.physics_object[0]).read(events).array

        eta1 = Eta(self.physics_object[1]).read(events).array
        phi1 = Phi(self.physics_object[1]).read(events).array

        if eta0.ndim == 3:
            eta0 = ak.flatten(eta0, axis=-1)
            phi0 = ak.flatten(phi0, axis=-1)

        if eta1.ndim == 3:
            eta1 = ak.flatten(eta1, axis=-1)
            phi1 = ak.flatten(phi1, axis=-1)

        if eta0.ndim == 1:
            eta0 = eta0[:, None]
            phi0 = phi0[:, None]

        if eta1.ndim == 1:
            eta1 = eta1[:, None]
            phi1 = phi1[:, None]

        delta_eta = eta0[:, :, None] - eta1[:, None, :]
        delta_phi = phi0[:, :, None] - phi1[:, None, :]
        array = np.hypot(delta_eta, delta_phi)
        return array

    @property
    def name(self) -> str:
        if self._name:
            return self._name

        physics_object = ",".join([obj.name for obj in self.physics_object])
        return f"{physics_object}.delta_r"

    @property
    def config(self) -> dict:
        config = super().config
        config["physics_object"] = [obj.name for obj in self.physics_object]
        return config

    @classmethod
    def from_config(cls, config: dict) -> Self:
        physics_object = config["physics_object"].split(",")
        name = config.get("name")
        return cls(physics_object=physics_object, name=name)
