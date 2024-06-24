import re
from typing import Literal, Self

import awkward as ak
import fastjet as fj
import uproot
import vector
from typeguard import typechecked

from ..events import DelphesEvent
from ..naming import str_to_index
from ..operations import fastjet_ops as fjo
from ..operations import uproot_ops as upo
from ..types import IndexLike
from .physics_object import PhysicsObjectBase

vector.register_awkward()


class Jet(PhysicsObjectBase):
    @typechecked
    def __init__(
        self,
        algorithm: Literal["kt", "ca", "ak"] | None = None,
        radius: float | None = None,
        key: str = "Jet",
        indices: IndexLike | list[IndexLike] | None = None,
    ) -> None:
        super().__init__(key, indices)
        self.algorithm = algorithm
        self.radius = radius

    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        if self.algorithm is None and self.radius is None:
            super().read(events)

            if "constituents" not in self.key.lower():
                self._values["charge"] = self.events[f"{self.key.lower()}.charge"]
                self._values["b_tag"] = self.events[f"{self.key.lower()}.b_tag"]
                self._values["tau_tag"] = self.events[f"{self.key.lower()}.tau_tag"]

        else:
            events = (
                DelphesEvent(events) if isinstance(events, uproot.TTree) else events
            )

            if "constituents" not in self.key.lower():
                key = f"{self.key.lower()}.constituents"
            else:
                key = self.key

            constituents_key = events.keys_dict[key]

            constituents = upo.constituents_to_momentum4d(events.tree[constituents_key])
            jet_def = fj.JetDefinition(fjo.get_algorithm(self.algorithm), self.radius)
            cluster = fj.ClusterSequence(ak.flatten(constituents, -1), jet_def)
            jets = ak.values_astype(cluster.inclusive_jets(), "float32")
            jets = ak.zip(
                {"pt": jets.pt, "eta": jets.eta, "phi": jets.phi, "mass": jets.mass},
                with_name="Momentum4D",
            )
            jets = jets[ak.argsort(jets.pt, ascending=False)]

            if "constituents" not in self.key.lower():
                self._values = jets
            else:
                self._values = ak.values_astype(cluster.constituents(), "float32")

        return self

    @property
    def name(self) -> str:
        name = super().name

        if self.algorithm is not None and self.radius is not None:
            name = f"{self.algorithm}{self.radius*10:.0f}{name}"

        return name

    @classmethod
    def from_name(cls, name: str) -> Self:
        names = name.split(".")
        match = re.fullmatch(r"(kt|ca|ak)?(\d+)?(.*[Jj]et)(\d*:?\d*)", names[0])
        algorithm, radius, key, indices = match.groups()
        radius = int(radius) / 10 if radius is not None else None
        indices = [str_to_index(indices)]

        if len(names) > 1:
            match = re.fullmatch(r"([Cc]onstituents)(\d*:?\d*)", names[1])
            branch2, slices2 = match.groups()
            key += "." + branch2
            indices += [str_to_index(slices2)]

        return cls(algorithm=algorithm, radius=radius, key=key, indices=indices)

    @property
    def config(self):
        config = super().config
        config["algorithm"] = self.algorithm
        config["radius"] = self.radius
        return config
