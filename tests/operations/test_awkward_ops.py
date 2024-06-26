from pathlib import Path

import awkward as ak
import numpy as np
import pytest

from hml.operations import awkward_ops as ako


def test_take():
    array = np.arange(15).reshape(3, 5)

    # Good
    assert ak.all(ako.take(array, 0, axis=1) == np.array([0, 5, 10]))
    assert ak.all(
        ako.take(array, slice(2), axis=1) == np.array([[0, 1], [5, 6], [10, 11]])
    )
    assert ako.take(array, [0, 1], axis=0) == 1
    assert ak.all(ako.take(array, [slice(1), slice(2)], axis=0) == np.array([[0, 1]]))

    # Bad
    with pytest.raises(ValueError):
        ako.take(array, [0, 1, 2], axis=0)
    with pytest.raises(ValueError):
        ako.take(array, [0, 1], axis=1)


def test_pad():
    array = ak.Array([[1, 2, 3], [1], [1, 2], []])

    # Good
    assert ak.all(ako.pad(array, [1, 2]) == array)
    assert ak.all(
        ako.pad(array, [1, slice(2)])
        == ak.Array([[1, 2], [1, None], [1, 2], [None, None]])
    )
    assert ak.all(ako.pad(array, [slice(2), slice(2)]) == ak.Array([[1, 2], [1, None]]))
    assert ak.all(
        ako.pad(array, [slice(5), slice(2)])
        == ak.Array([[1, 2], [1, None], [1, 2], [None, None], None])
    )

    # Bad
    with pytest.raises(ValueError):
        ako.pad(array, [1, 2, 3])
    with pytest.raises(ValueError):
        ako.pad(array, [slice(None), slice(None), slice(None)], axis=1)


def test_squeeze():
    array = ak.from_numpy(np.array([[[1, 2, 3]], [[4, 5, 6]]]))
    assert ako.squeeze(array).typestr == "2 * 3 * int64"
    assert ako.squeeze(array, axis=1).typestr == "2 * 3 * int64"

    array = ak.Array([[[1, 2]], [[1]], [[1, 2, 3]]])
    assert ako.squeeze(array).typestr == "3 * var * int64"

    array = ak.Array([[1]])
    assert ako.squeeze(array) == 1
    assert ako.squeeze(array, axis=0).typestr == "1 * int64"

    array = ak.Array([[[1]]])
    assert ako.squeeze(array) == 1
    assert ako.squeeze(array, axis=0).typestr == "1 * var * int64"

    # Bad
    array = ak.Array([1])
    with pytest.raises(ValueError):
        ako.squeeze(array, 1)


def test_to_and_from_hdf5():
    filepath = Path("/tmp/test.h5")
    filepath.unlink(missing_ok=True)

    array = ak.from_numpy(np.random.randint(0, 10, size=(10000, 5)))
    ako.to_hdf5(array, filepath, piece_size=1000)
    ako.to_hdf5(array, filepath, piece_size=1000, verbose=1)

    assert filepath.exists()

    loaded_array = ako.from_hdf5(filepath)
    loaded_array = ako.from_hdf5(filepath, verbose=1)

    assert ak.all(array == loaded_array)
