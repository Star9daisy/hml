import awkward as ak
import uproot

from .builtins import Path

PathLike = Path | str
ROOTEvents = uproot.TTree
AwkwardArray = ak.Array
