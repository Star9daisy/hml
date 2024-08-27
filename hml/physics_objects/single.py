import awkward as ak
from typeguard import typechecked

from ..events import ROOTEvents
from ..naming import INDEX_PATTERN
from ..saving import registered_object
from ..types import AwkwardArray
from .physics_object import Single


@typechecked
@registered_object(f"electron{INDEX_PATTERN}")
class Electron(Single):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.pt"]),
                "charge": events[f"{self.key}.charge"],
            }
        )

        return array


@typechecked
@registered_object(f"jet{INDEX_PATTERN}")
class Jet(Single):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        n_subjettiness = events[self.key + ".tau[5]"]

        array = ak.zip(
            {
                "pt": events[self.key + ".pt"],
                "eta": events[self.key + ".eta"],
                "phi": events[self.key + ".phi"],
                "mass": events[self.key + ".mass"],
                "b_tag": events[self.key + ".b_tag"],
                "tau_tag": events[self.key + ".tau_tag"],
                "charge": events[self.key + ".charge"],
                "tau1": n_subjettiness[..., 0],
                "tau2": n_subjettiness[..., 1],
                "tau3": n_subjettiness[..., 2],
                "tau4": n_subjettiness[..., 3],
                "tau5": n_subjettiness[..., 4],
            }
        )

        return array


@typechecked
@registered_object(f"missing_et{INDEX_PATTERN}")
@registered_object(f"met{INDEX_PATTERN}")
class MissingET(Single):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.met"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.met"]),
            }
        )

        return array


@typechecked
@registered_object(f"muon{INDEX_PATTERN}")
class Muon(Single):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.pt"]),
                "charge": events[f"{self.key}.charge"],
            }
        )

        return array


@typechecked
@registered_object(f"photon{INDEX_PATTERN}")
class Photon(Single):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.pt"]),
            }
        )

        return array


@typechecked
@registered_object(f"tower{INDEX_PATTERN}")
class Tower(Single):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.et"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.et"]),
            }
        )

        return array


@typechecked
@registered_object(f"track{INDEX_PATTERN}")
class Track(Single):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": events[f"{self.key}.mass"],
            }
        )

        return array
