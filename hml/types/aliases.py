from pathlib import Path

from .externals import AwkwardArray, NumpyArray

Index = int | slice
PathLike = str | Path
ArrayLike = AwkwardArray | NumpyArray
