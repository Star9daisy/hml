from pathlib import Path

from .externals import AwkwardArray, NumpyArray

Index = int | slice
PathLike = str | Path
ArrayLike = AwkwardArray | NumpyArray


class VariableInteger(int):
    """Variable integer type"""

    def __str__(self) -> str:
        return "var"

    def __repr__(self) -> str:
        return "var"


var = VariableInteger()
