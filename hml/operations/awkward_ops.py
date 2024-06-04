from __future__ import annotations

import math
from pathlib import Path

import awkward as ak
import h5py
import numpy as np
from tqdm import tqdm


def ak_to_h5(
    array: ak.Array,
    path: str | Path,
    chunk_size: int | None = None,
    verbose: int = 0,
):
    """Save an Awkward Array to an HDF5 file.

    Parameters
    ----------
    array : ak.Array
        The array to save.
    path : str or Path
        The path to the HDF5 file.
    chunk_size : int or None, optional
        If not None, the array will be saved in chunks of the specified size.
    verbose : int, optional
        If 1, show a progress bar.

    Examples
    --------
    >>> import awkward as ak
    >>> from hml.operations import ak_to_h5
    >>> array = ak.Array([[1, 2, 3], [], [4, 5], [], [], [6, 7, 8, 9]])
    >>> ak_to_h5(array, "/tmp/array.h5")
    """
    with h5py.File(path, "w") as file:
        group = file.create_group("awkward")
        group.attrs["total_size"] = len(array)

        chunk_size = 0 if chunk_size is None else chunk_size
        group.attrs["chunk_size"] = chunk_size

        if chunk_size == 0:
            form, length, _ = ak.to_buffers(array, container=group)
            group.attrs["form"] = form.to_json()
            group.attrs["length"] = length

        else:
            total_size = len(array)
            chunk_starts = range(0, total_size, chunk_size)
            chunks = [slice(i, i + chunk_size) for i in chunk_starts]

            if verbose == 1:
                iterator = tqdm(enumerate(chunks), total=len(chunks))
            else:
                iterator = enumerate(chunks)

            for i, slice_ in iterator:
                subgroup = group.create_group(f"chunk_{i}")
                array_chunk = array[slice_]

                packed_array = ak.to_packed(array_chunk)
                form, length, _ = ak.to_buffers(packed_array, subgroup)
                subgroup.attrs["form"] = form.to_json()
                subgroup.attrs["length"] = length


def ak_from_h5(
    path: str | Path,
    chunks: list[int] | None = None,
    verbose: int = 0,
):
    """Load an Awkward Array from an HDF5 file.

    Parameters
    ----------
    path : str or Path
        The path to the HDF5 file.
    chunks : list of int or None, optional
        Chunk indices to load. If None, load all chunks if the array was saved
        in chunks.
    verbose : int, optional
        If 1, show a progress bar.

    Examples
    --------
    >>> from hml.operations import ak_to_h5, ak_from_h5
    >>> array = ak.Array([[1, 2, 3], [], [4, 5], [], [], [6, 7, 8, 9]])
    >>> ak_to_h5(array, "/tmp/array.h5")
    >>> array = ak_from_h5("/tmp/array.h5")
    """
    with h5py.File(path, "r") as file:
        group = file["awkward"]

        if group.attrs["chunk_size"] == 0:
            array = ak.from_buffers(
                form=ak.forms.from_json(group.attrs["form"]),
                length=group.attrs["length"],
                container={k: np.asarray(v) for k, v in group.items()},
            )

        else:
            if chunks is None:
                n_chunks = group.attrs["total_size"] / group.attrs["chunk_size"]
                n_chunks = math.ceil(n_chunks)
                chunks = range(n_chunks)

            if verbose:
                iterator = tqdm(chunks)
            else:
                iterator = chunks

            array = []
            for i in iterator:
                subgroup = group[f"chunk_{i}"]
                array_chunk = ak.from_buffers(
                    form=ak.forms.from_json(subgroup.attrs["form"]),
                    length=subgroup.attrs["length"],
                    container={k: np.asarray(v) for k, v in subgroup.items()},
                )
                array.append(array_chunk)

            array = ak.concatenate(array)

    return array
