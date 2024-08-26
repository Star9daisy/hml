import awkward as ak

from hml.operations.awkward_ops import pad_none


def test_pad_none():
    numbers = ak.Array([[1, 2], [1], [1, 2, 3]])

    assert pad_none(numbers, 3, 0).typestr == "3 * var * int64"
    assert pad_none(numbers, 4, 0).typestr == "4 * var * ?int64"
    assert pad_none(numbers, 1, 1).typestr == "3 * 1 * int64"
    assert pad_none(numbers, 3, 1).typestr == "3 * 3 * ?int64"

    records = ak.zip(
        {
            "x": [[1, 2], [1], [1, 2, 3]],
            "y": [[1, 2], [1], [1, 2, 3]],
        }
    )

    assert pad_none(records, 3, 0).typestr == "3 * var * {x: int64, y: int64}"
    assert pad_none(records, 4, 0).typestr == "4 * var * ?{x: int64, y: int64}"
    assert pad_none(records, 1, 1).typestr == "3 * 1 * {x: int64, y: int64}"
    assert pad_none(records, 3, 1).typestr == "3 * 3 * ?{x: int64, y: int64}"
