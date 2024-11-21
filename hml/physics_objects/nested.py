import awkward as ak
from typeguard import typechecked

from ..operations.fastjet import get_inclusive_jets
from ..operations.uproot import get_branch
from ..types import Self, UprootTree, momentum_to_array, pxpypze_to_ptetaphimass
from .base import NestedPhysicsObject, SinglePhysicsObject
from .single import FatJet, Jet


@typechecked
class Reclustered(NestedPhysicsObject):
    def __init__(
        self,
        branch: SinglePhysicsObject,
        class_name: str = "reclustered",
    ) -> None:
        super().__init__(branch=branch, class_name=class_name)

        if not isinstance(branch, (FatJet, Jet)):
            raise TypeError("Currently only fat jets and jets are supported")

        if not branch.algorithm or not branch.radius:
            raise ValueError("Algorithm and radius must be set")

    def read(self, events: UprootTree) -> Self:
        branch = f"{self.branch.branch}.Constituents"
        constituents = get_branch(events, branch, as_momentum=True)

        jets, constituents = get_inclusive_jets(
            constituents,
            radius=self.branch.radius,
            algorithm=self.branch.algorithm,
            return_constituents=True,
        )

        jets = momentum_to_array(pxpypze_to_ptetaphimass(jets))
        constituents = momentum_to_array(pxpypze_to_ptetaphimass(constituents))

        self.array = ak.values_astype(jets, "float32")
        self.constituents = ak.values_astype(constituents, "float32")

        return self

    @classmethod
    def from_name(cls, name: str) -> Self:
        branch_name, class_name = name.split(".")

        if branch_name.endswith("fatjet"):
            branch = FatJet.from_name(branch_name)
        elif branch_name.endswith("jet"):
            branch = Jet.from_name(branch_name)
        else:
            raise ValueError(f"Invalid branch name: {branch_name}")

        return cls(branch=branch, class_name=class_name)


@typechecked
class Constituents(NestedPhysicsObject):
    def __init__(
        self,
        branch: SinglePhysicsObject | NestedPhysicsObject,
        class_name: str = "constituents",
    ) -> None:
        super().__init__(branch=branch, class_name=class_name)

        if not isinstance(branch, (FatJet, Jet, Reclustered)):
            raise TypeError(
                "Currently only fat jets, jets and reclustered jets are supported"
            )

    def read(self, events: UprootTree) -> Self:
        self.branch.read(events)
        self.array = self.branch.constituents

        return self

    @classmethod
    def from_name(cls, name: str) -> Self:
        branch_name, class_name = name.rsplit(".", 1)

        if branch_name.endswith("reclustered"):
            branch = Reclustered.from_name(branch_name)
        elif branch_name.endswith("fatjet"):
            branch = FatJet.from_name(branch_name)
        elif branch_name.endswith("jet"):
            branch = Jet.from_name(branch_name)
        else:
            raise ValueError(f"Invalid branch name: {branch_name}")

        return cls(branch=branch, class_name=class_name)
