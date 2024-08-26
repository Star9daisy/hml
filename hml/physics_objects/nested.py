import re

import awkward as ak
from typeguard import typechecked

from ..events import ROOTEvents
from ..operations.uproot_ops import constituents_to_momentum4d
from ..saving import registered_object
from ..types import AwkwardArray
from .physics_object import Nested


@typechecked
@registered_object(re.compile("constituents(\d*:?\d*)"), is_for_init=True)
class Constituents(Nested):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        original_key = events.mappings[".".join(self.keys)]
        array = constituents_to_momentum4d(events.tree[original_key])
        array = ak.zip(
            {
                "pt": array.pt,
                "eta": array.eta,
                "phi": array.phi,
                "mass": array.mass,
            }
        )

        return array
