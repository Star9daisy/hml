from .builtins import Path
from .externals import uproot

PathLike = Path | str
ROOTEvents = uproot.TTree
