from __future__ import annotations

import math
from pathlib import Path

import awkward as ak
import h5py
import numpy as np
from tqdm import tqdm

from ..types import ArrayLike, IndexLike


def take(
    array: ArrayLike,
    indices: IndexLike | list[IndexLike],
    axis: int = 0,
) -> ArrayLike:
    """Take data from an array starting from a given axis.

    Parameters
    ----------
    array : ArrayLike
        The array to take data from.
    indices : IndexLike or list of IndexLike
        The indices to take. Both integers and slices are supported.
    axis : int, optional
        The axis to start taking data from.

    Returns
    -------
    ArrayLike
        The taken data.

    Raises
    ------
    ValueError
        If too many indices are given starting from the axis.

    Examples
    --------
    >>> import numpy as np
    >>> from hml.operations import awkward_ops as ako

    >>> array = np.arange(15).reshape(3, 5)
    >>> array
    array([[ 0,  1,  2,  3,  4],
           [ 5,  6,  7,  8,  9],
           [10, 11, 12, 13, 14]])

    >>> ako.take(array, 1, axis=1)
    array([ 1,  6, 11])
    >>> array[:, 1] # equivalent to the above
    array([ 1,  6, 11])

    >>> ako.take(array, slice(1, 3), axis=1)
    array([[ 1,  2],
           [ 6,  7],
           [11, 12]])
    >>> array[:, 1:3] # equivalent to the above
    array([[ 1,  2],
           [ 6,  7],
           [11, 12]])

    >>> ako.take(array, [1, 3], axis=0)
    8
    >>> array[1, 3] # equivalent to the above
    8

    >>> ako.take(array, [slice(1, 3), 3], axis=0)
    array([ 8, 13])
    >>> array[1:3, 3] # equivalent to the above
    array([ 8, 13])
    """
    indices = [indices] if not isinstance(indices, list) else indices
    if axis + len(indices) > array.ndim:
        raise ValueError("Too many indices starting from the given axis.")

    slices = [slice(None) for _ in range(array.ndim)]
    slices[axis:] = indices
    return array[*slices]


def pad(
    array: ArrayLike,
    indices: list[IndexLike],
    clip: bool = True,
    axis: int = 0,
) -> ak.Array:
    """Pad an array with None values to match the given indices.

    Parameters
    ----------
    array : ArrayLike
        The array to pad.
    indices : list of IndexLike
        The indices to get the required length to pad the array.
    axis: int
        The axis to start padding from.

    Returns
    -------
    ak.Array
        The padded array.

    Examples
    --------
    >>> import awkward as ak
    >>> from hml.operations import awkward_ops as ako

    >>> array = ak.Array([[1, 2], [], [1, 2, 3]])
    >>> print(ako.pad(array, [slice(4)]))
    [[1, 2], [], [1, 2, 3], None]

    >>> print(ako.pad(array, [slice(4), slice(3)]))
    [[1, 2, None], [None, None, None], [1, 2, 3], None]
    """
    if len(indices) + axis > array.ndim:
        raise ValueError("Too many indices starting from the given axis.")

    array = array[axis:]

    for i, index in enumerate(indices):
        if isinstance(index, slice):
            if index.stop is not None:
                required_length = index.stop - (index.start or 0)
                array = ak.pad_none(array, required_length, axis=i, clip=True)

    return array


def squeeze(array: ak.Array, axis: int | None = None) -> ak.Array:
    """Remove single-dimensional entries from an array.

    Parameters
    ----------
    array : ak.Array
        The array to squeeze.
    axis : int or None, optional
        The axis to be squeezed. If None, squeeze all axes.

    Returns
    -------
    ak.Array
        The squeezed array.

    Examples
    --------
    >>> import awkward as ak
    >>> from hml.operations import awkward_ops as ako

    >>> array = ak.Array([[[1, 2, 3]], [[4, 5, 6]]])
    >>> array = ak.to_regular(array, None)
    >>> array.typestr
    '2 * 1 * 3 * int64'
    >>> ako.squeeze(array).typestr
    '2 * 3 * int64'

    >>> array = ak.Array([[[1, 2]], [[1]], [[1, 2, 3]]])
    >>> ak.to_regular(array, 1).typestr
    '3 * 1 * var * int64'
    >>> ako.squeeze(array).typestr
    '3 * var * int64'

    >>> array = ak.Array([[1]])
    >>> ak.to_regular(array, None).typestr
    '1 * 1 * int64'
    >>> ako.squeeze(array)
    1
    >>> ako.squeeze(array, 0).typestr
    '1 * int64'
    """
    if axis is not None and axis >= array.ndim:
        raise ValueError(
            f"axis {axis} is out of bounds for array with {array.ndim} dimensions"
        )

    if axis is None:
        axes = range(array.ndim)
    else:
        axes = [axis]

    offset = 0
    for axis in axes:
        axis -= offset
        try:
            if ak.to_regular(array, axis).typestr.split(" * ")[axis] == "1":
                array = take(array, 0, axis)
                offset += 1
        except Exception:
            pass

    return array


def to_hdf5(
    array: ak.Array,
    path: str | Path,
    piece_size: int | None = None,
    verbose: int = 0,
):
    """Save an Awkward Array to an HDF5 file.

    Parameters
    ----------
    array : ak.Array
        The array to save.
    path : str or Path
        The path to the HDF5 file.
    piece_size : int or None, optional
        If not None, the array will be saved in pieces of the specified size.
    verbose : int, optional
        If 1, show a progress bar.

    Examples
    --------
    >>> import awkward as ak
    >>> from hml.operations import awkward_ops as ako

    >>> array = ak.Array([[1, 2, 3], [], [4, 5], [], [], [6, 7, 8, 9]])
    >>> ako.to_hdf5(array, "/tmp/array.h5")

    >>> from pathlib import Path
    >>> Path("tests/data/pp2zz/Events/run_01/tag_1_delphes_events.root").exists()
    True
    """
    with h5py.File(path, "w") as file:
        group = file.create_group("awkward")
        group.attrs["total_size"] = len(array)

        piece_size = 0 if piece_size is None else piece_size
        group.attrs["piece_size"] = piece_size

        if piece_size == 0:
            form, length, _ = ak.to_buffers(array, container=group)
            group.attrs["form"] = form.to_json()
            group.attrs["length"] = length

        else:
            total_size = len(array)
            piece_starts = range(0, total_size, piece_size)
            pieces = [slice(i, i + piece_size) for i in piece_starts]

            if verbose == 1:
                iterator = tqdm(enumerate(pieces), total=len(pieces))
            else:
                iterator = enumerate(pieces)

            for i, slice_ in iterator:
                subgroup = group.create_group(f"piece_{i}")
                array_piece = array[slice_]

                packed_array = ak.to_packed(array_piece)
                form, length, _ = ak.to_buffers(packed_array, subgroup)
                subgroup.attrs["form"] = form.to_json()
                subgroup.attrs["length"] = length


def from_hdf5(
    path: str | Path,
    pieces: list[int] | None = None,
    verbose: int = 0,
):
    """Load an Awkward Array from an HDF5 file.

    Parameters
    ----------
    path : str or Path
        The path to the HDF5 file.
    pieces : list of int or None, optional
        Piece indices to load. If None, load all pieces if the array was saved
        in pieces.
    verbose : int, optional
        If 1, show a progress bar.

    Examples
    --------
    >>> import hml.operations.awkward_ops as ako

    >>> array = ak.Array([[1, 2, 3], [], [4, 5], [], [], [6, 7, 8, 9]])
    >>> ako.to_hdf5(array, "/tmp/array.h5")
    >>> array = ako.from_hdf5("/tmp/array.h5")
    """
    with h5py.File(path, "r") as file:
        group = file["awkward"]

        if group.attrs["piece_size"] == 0:
            array = ak.from_buffers(
                form=ak.forms.from_json(group.attrs["form"]),
                length=group.attrs["length"],
                container={k: np.asarray(v) for k, v in group.items()},
            )

        else:
            if pieces is None:
                n_pieces = group.attrs["total_size"] / group.attrs["piece_size"]
                n_pieces = math.ceil(n_pieces)
                pieces = range(n_pieces)

            if verbose:
                iterator = tqdm(pieces)
            else:
                iterator = pieces

            array = []
            for i in iterator:
                subgroup = group[f"piece_{i}"]
                array_piece = ak.from_buffers(
                    form=ak.forms.from_json(subgroup.attrs["form"]),
                    length=subgroup.attrs["length"],
                    container={k: np.asarray(v) for k, v in subgroup.items()},
                )
                array.append(array_piece)

            array = ak.concatenate(array)

    return array
