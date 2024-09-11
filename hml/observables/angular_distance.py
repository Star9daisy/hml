import awkward as ak
import numpy as np
from typeguard import typechecked

from ..events import Events
from ..physics_objects import PhysicsObject
from ..saving import registered_object
from ..types import AwkwardArray
from .observable import Observable


@typechecked
@registered_object(r"(?P<physics_object>[\w:._]+(?:,[\w:._]+)+)\.(DeltaR|delta_r)")
class DeltaR(Observable):
    def __init__(self, physics_object: list[PhysicsObject], **kwargs) -> None:
        super().__init__(physics_object, **kwargs)
        name = kwargs.get("name")
        physics_object_names = ",".join([obj.name for obj in self.physics_object])
        self._name = name if name is not None else f"{physics_object_names}.delta_r"

        if len(physics_object) != 2:
            raise ValueError("DeltaR requires exactly two physics objects.")

    def get_array(self, events: Events) -> AwkwardArray:
        self.physics_object[0].read(events)
        self.physics_object[1].read(events)
        eta1 = self.physics_object[0].array.eta
        phi1 = self.physics_object[0].array.phi
        eta2 = self.physics_object[1].array.eta
        phi2 = self.physics_object[1].array.phi

        if eta1.ndim > 2:
            for _ in range(eta1.ndim - 2):
                eta1 = ak.flatten(eta1, axis=-1)
                phi1 = ak.flatten(phi1, axis=-1)
                try:
                    eta1 = ak.to_regular(eta1, axis=-1)
                    phi1 = ak.to_regular(phi1, axis=-1)
                except Exception:  # pragma: no cover
                    pass

        if eta2.ndim > 2:
            for _ in range(eta2.ndim - 2):
                eta2 = ak.flatten(eta2, axis=-1)
                phi2 = ak.flatten(phi2, axis=-1)
                try:
                    eta2 = ak.to_regular(eta2, axis=-1)
                    phi2 = ak.to_regular(phi2, axis=-1)
                except Exception:  # pragma: no cover
                    pass

        if eta1.ndim == 2 and eta2.ndim == 2:
            eta1 = eta1[:, :, None]
            phi1 = phi1[:, :, None]
            eta2 = eta2[:, None, :]
            phi2 = phi2[:, None, :]

        if eta1.ndim == 1:
            eta1 = eta1[:, *([None] * (eta2.ndim - 1))]
            phi1 = phi1[:, *([None] * (eta2.ndim - 1))]

        if eta2.ndim == 1:
            eta2 = eta2[:, *([None] * (eta1.ndim - 1))]
            phi2 = phi2[:, *([None] * (eta1.ndim - 1))]

        array = np.hypot(eta1 - eta2, phi1 - phi2)
        return array
