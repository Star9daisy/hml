import awkward as ak
from typeguard import typechecked

from ..types import AwkwardArray


@typechecked
def pad_none(array: AwkwardArray, target: int, axis: int = 1) -> AwkwardArray:
    """Pad an array with None values to have a regular shape.

    Parameters
    ----------
    array : AwkwardArray
        An awkward array, either numbers or records.
    target : int
        The target size of the array at the target axis.
    axis : int, optional
        The axis to pad the array. Default is 1.

    Returns
    -------
    AwkwardArray
    """
    # Convert the negative axis to a positive one.
    axis = axis if axis >= 0 else array.ndim + axis

    # Check if the array has enough elements at the target axis.
    n_elements = ak.num(array, axis)
    n_elements = n_elements if axis > 0 else ak.from_iter([n_elements])

    if ak.all(target <= n_elements):
        # Slice the array if it has enough elements at the target axis.
        slice_ = [slice(None)] * array.ndim
        slice_[axis] = slice(target)
        sliced = array[tuple(slice_)]
        return ak.to_regular(sliced, axis=axis)

    # The type "optional" appears if the array does not have enough elements at
    # some axis when padding it with a larger target size.
    padded = ak.pad_none(array, target, axis=axis, clip=True)

    # Calculate the shape of None values that will keep the "?" mark at the
    # deepest level.
    if array.ndim - axis - 1 > 0:
        none_values = [None] * (array.ndim - axis - 1)
        return ak.fill_none(padded, value=none_values, axis=axis)
    else:
        return padded
