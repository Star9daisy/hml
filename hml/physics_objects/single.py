import awkward as ak
from particle import Particle
from typeguard import typechecked

from ..operations.fastjet import get_inclusive_jets
from ..operations.uproot import get_branch
from ..types import (
    JET_ALGORITHM,
    Self,
    UprootTree,
    momentum_to_array,
    pxpypze_to_ptetaphimass,
)
from .base import SinglePhysicsObject


@typechecked
class Electron(SinglePhysicsObject):
    MASS = Particle.from_name("e-").mass

    def __init__(self, branch: str = "Electron", class_name: str = "electron") -> None:
        super().__init__(branch=branch, class_name=class_name)

    def read(self, events: UprootTree) -> Self:
        self.array = ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "mass": ak.full_like(events[f"{self.branch}.PT"].array(), self.MASS),
                "charge": events[f"{self.branch}.Charge"].array(),
            }
        )

        return self


@typechecked
class Jet(SinglePhysicsObject):
    def __init__(
        self,
        algorithm: JET_ALGORITHM | None = None,
        radius: float | None = None,
        branch: str = "Jet",
        class_name: str = "jet",
    ) -> None:
        super().__init__(branch=branch, class_name=class_name)
        self.algorithm = algorithm
        self.radius = radius

    def read(self, events: UprootTree) -> Self:
        if not self.algorithm or not self.radius:
            n_subjettiness = events[f"{self.branch}.Tau[5]"].array()

            self.array = ak.zip(
                {
                    "pt": events[f"{self.branch}.PT"].array(),
                    "eta": events[f"{self.branch}.Eta"].array(),
                    "phi": events[f"{self.branch}.Phi"].array(),
                    "mass": events[f"{self.branch}.Mass"].array(),
                    "b_tag": events[f"{self.branch}.BTag"].array(),
                    "tau_tag": events[f"{self.branch}.TauTag"].array(),
                    "charge": events[f"{self.branch}.Charge"].array(),
                    "tau1": n_subjettiness[..., 0],
                    "tau2": n_subjettiness[..., 1],
                    "tau3": n_subjettiness[..., 2],
                    "tau4": n_subjettiness[..., 3],
                    "tau5": n_subjettiness[..., 4],
                }
            )

            branch = f"{self.branch}.Constituents"
            constituents = get_branch(events, branch)
            self.constituents = ak.values_astype(constituents, "float32")

            return self

        branch = f"{self.branch}.Constituents"
        constituents = get_branch(events, branch, as_momentum=True)
        flattened_constituents = ak.flatten(constituents, axis=-1)

        jets, constituents = get_inclusive_jets(
            flattened_constituents,
            radius=self.radius,
            algorithm=self.algorithm,
            return_constituents=True,
        )
        jets = momentum_to_array(pxpypze_to_ptetaphimass(jets))
        constituents = momentum_to_array(pxpypze_to_ptetaphimass(constituents))

        self.array = ak.values_astype(jets, "float32")
        self.constituents = ak.values_astype(constituents, "float32")

        return self

    @property
    def name(self) -> str:
        if self.algorithm and self.radius:
            prefix = f"{self.algorithm}{self.radius*10:.0f}"
        else:
            prefix = ""

        return prefix + super().name

    @classmethod
    def from_name(cls, name: str) -> Self:
        if name == "jet":
            return cls()

        algorithm = name[:2]
        radius = float(name[2:-3]) / 10

        return cls(algorithm=algorithm, radius=radius)

    @property
    def config(self) -> dict:
        config = super().config
        config["algorithm"] = self.algorithm
        config["radius"] = self.radius

        return config

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(
            algorithm=config["algorithm"],
            radius=config["radius"],
            branch=config["branch"],
            class_name=config["class_name"],
        )


@typechecked
class FatJet(Jet):
    def __init__(
        self,
        algorithm: JET_ALGORITHM | None = None,
        radius: float | None = None,
        branch: str = "FatJet",
        class_name: str = "fatjet",
    ) -> None:
        super().__init__(
            algorithm=algorithm,
            radius=radius,
            branch=branch,
            class_name=class_name,
        )

    @classmethod
    def from_name(cls, name: str) -> Self:
        if name == "fatjet":
            return cls()

        algorithm = name[:2]
        radius = float(name[2:-6]) / 10

        return cls(algorithm=algorithm, radius=radius)


@typechecked
class MissingET(SinglePhysicsObject):
    def __init__(self, branch: str = "MissingET", class_name: str = "met") -> None:
        super().__init__(branch=branch, class_name=class_name)

    def read(self, events: UprootTree) -> Self:
        self.array = ak.zip(
            {
                "pt": events[f"{self.branch}.MET"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "mass": ak.zeros_like(events[f"{self.branch}.MET"].array()),
            }
        )

        return self


@typechecked
class Muon(SinglePhysicsObject):
    MASS = Particle.from_name("mu-").mass

    def __init__(self, branch: str = "Muon", class_name: str = "muon") -> None:
        super().__init__(branch=branch, class_name=class_name)

    def read(self, events: UprootTree) -> Self:
        self.array = ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "mass": ak.full_like(events[f"{self.branch}.PT"].array(), self.MASS),
                "charge": events[f"{self.branch}.Charge"].array(),
            }
        )

        return self


@typechecked
class Photon(SinglePhysicsObject):
    def __init__(self, branch: str = "Photon", class_name: str = "photon") -> None:
        super().__init__(branch=branch, class_name=class_name)

    def read(self, events: UprootTree) -> Self:
        self.array = ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "mass": ak.zeros_like(events[f"{self.branch}.PT"].array()),
            }
        )

        return self


@typechecked
class Tower(SinglePhysicsObject):
    def __init__(self, branch: str = "Tower", class_name: str = "tower") -> None:
        super().__init__(branch=branch, class_name=class_name)

    def read(self, events: UprootTree) -> Self:
        self.array = ak.zip(
            {
                "pt": events[f"{self.branch}.ET"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "mass": ak.zeros_like(events[f"{self.branch}.ET"].array()),
            }
        )

        return self


@typechecked
class Track(SinglePhysicsObject):
    def __init__(self, branch: str = "Track", class_name: str = "track") -> None:
        super().__init__(branch=branch, class_name=class_name)

    def read(self, events: UprootTree) -> Self:
        self.array = ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "mass": events[f"{self.branch}.Mass"].array(),
            }
        )

        return self
