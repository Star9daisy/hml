import awkward as ak
import pytest

from hml.operations.awkward import (
    NumberArray,
    RecordArray,
    VectorArray,
    convert_to_array,
    convert_to_regular_array,
    create_nested_list,
    pad_none_according_to_indices,
    pad_none_keeping_structure,
)


def test_convert_to_regular_array():
    array = ak.Array([[1, 2, 3], [1, 2], [1]])
    expected_typestr = "3 * var * int64"
    regular_array = convert_to_regular_array(array)
    assert regular_array.typestr == expected_typestr

    array = ak.Array([[], [], []])
    expected_typestr = "3 * 0 * unknown"
    regular_array = convert_to_regular_array(array)
    assert regular_array.typestr == expected_typestr


def test_create_nested_list():
    level = 0
    expected = [None]
    nested_list = create_nested_list(level)
    assert nested_list == expected

    level = 1
    expected = [[None]]
    nested_list = create_nested_list(level)
    assert nested_list == expected

    level = 2
    expected = [[[None]]]
    nested_list = create_nested_list(level)
    assert nested_list == expected


def test_pad_none_keeping_structure():
    array = ak.Array([[1, 2], [1], []])
    target = 2
    axis = 0
    expected_typestr = "2 * var * int64"
    padded_array = pad_none_keeping_structure(array, target, axis)
    assert padded_array.typestr == expected_typestr

    array = ak.Array([[1, 2], [1], []])
    target = 3
    axis = 0
    expected_typestr = "3 * var * int64"
    padded_array = pad_none_keeping_structure(array, target, axis)
    assert padded_array.typestr == expected_typestr

    array = ak.Array([[1, 2], [1], []])
    target = 4
    axis = 0
    expected_typestr = "4 * var * ?int64"
    padded_array = pad_none_keeping_structure(array, target, axis)
    assert padded_array.typestr == expected_typestr

    array = ak.Array([[1, 2], [1], []])
    target = 2
    axis = 1
    expected_typestr = "3 * 2 * ?int64"
    padded_array = pad_none_keeping_structure(array, target, axis)
    assert padded_array.typestr == expected_typestr


def test_pad_none_according_to_indices():
    array = ak.Array([[1, 2], [1], []])
    indices = (slice(None), slice(None))
    expected_typestr = "3 * var * int64"
    padded_array = pad_none_according_to_indices(array, indices)
    assert padded_array.typestr == expected_typestr

    array = ak.Array([[1, 2], [1], []])
    indices = (slice(None), 0)
    expected_typestr = "3 * 1 * ?int64"
    padded_array = pad_none_according_to_indices(array, indices)
    assert padded_array.typestr == expected_typestr

    array = ak.Array([[1, 2], [1], []])
    indices = (slice(None), slice(3))
    expected_typestr = "3 * 3 * ?int64"
    padded_array = pad_none_according_to_indices(array, indices)
    assert padded_array.typestr == expected_typestr

    array = ak.Array([[1, 2], [1], []])
    indices = (slice(None), slice(3, None))
    expected_typestr = "3 * var * int64"
    padded_array = pad_none_according_to_indices(array, indices)
    assert padded_array.typestr == expected_typestr


def test_convert_to_array():
    object_ = [[1, 2, 3], [1, 2], [1]]
    expected = ak.Array(object_)
    array = convert_to_array(object_)
    assert ak.all(array == expected)

    object_ = ak.pad_none(ak.Array([[1, 2, 3], [1, 2], [1]]), 3, axis=0)
    expected_typestr = "3 * var * int64"
    array = convert_to_array(object_)
    assert array.typestr == expected_typestr

    object_ = ak.Array([[1, 2, 3], [1, 2], [1]])
    array = convert_to_array(object_)
    assert ak.all(array == object_)


def test_number_array_init():
    _ = NumberArray([[1, 2, 3], [1, 2], [1]])

    with pytest.raises(ValueError):
        NumberArray(ak.zip({"px": [[1, 2, 3], [1, 2], [1]]}))


def test_number_array_repr():
    array = ak.Array([1, 2])
    expected = "[1,\n 2]\n---------------\ntype: 2 * int64"
    numbers = NumberArray(array)
    assert repr(numbers) == expected


def test_number_array_getitem():
    array = ak.Array([[1, 2, 3], [1, 2], [1]])
    numbers = NumberArray(array)
    numbers = numbers[:, 0]

    assert isinstance(numbers, NumberArray)


def test_number_array_shape():
    array = ak.Array([[1, 2, 3], [1, 2], [1]])
    numbers = NumberArray(array)
    assert numbers.shape == (3, "var")

    array = ak.Array([[1, 2, 3], [1, 2], [1]])
    padded = ak.pad_none(array, 3, axis=0)
    numbers = NumberArray(padded)

    assert numbers.shape == (3, "var")

    array = ak.Array([[], [], []])
    numbers = NumberArray(array)

    assert numbers.shape == (3, 0)


def test_number_array_dtype():
    array = ak.Array([[1, 2, 3], [1, 2], [1]])
    numbers = NumberArray(array)

    assert numbers.dtype == "int64"

    array = ak.Array([[], [], []])
    numbers = NumberArray(array)

    assert numbers.dtype == "unknown"


def test_record_array_init():
    _ = RecordArray({"px": [[1, 2, 3], [1, 2], [1]]})
    _ = RecordArray(ak.zip({"px": [[1, 2, 3], [1, 2], [1]]}))
    _ = RecordArray(ak.zip({"px": [[], [], []]}))

    with pytest.raises(ValueError):
        RecordArray(ak.Array([[1, 2, 3], [1, 2], [1]]))


def test_record_array_repr():
    array = ak.zip({"px": [1, 2]})
    expected = "[{px: 1},\n {px: 2}]\n-------------\ntype: 2 * {\n    px: int64\n}"
    records = RecordArray(array)

    assert repr(records) == expected


def test_record_array_getitem():
    array = ak.zip({"px": [[1, 2, 3], [1, 2], [1]]})
    records = RecordArray(array)
    records = records["px"]

    assert isinstance(records, NumberArray)

    array = ak.zip({"px": [[1, 2, 3], [1, 2], [1]]})
    records = RecordArray(array)
    records = records[:, 0]

    assert isinstance(records, RecordArray)


def test_record_array_shape():
    array = ak.zip({"px": [[1, 2, 3], [1, 2], [1]]})
    records = RecordArray(array)

    assert records.shape == (3, "var")

    array = ak.zip({"px": ak.Array([[1, 2, 3], [1, 2], [1]])})
    padded = ak.pad_none(array, 3, axis=0)
    records = RecordArray(padded)

    assert records.shape == (3, "var")

    array = ak.zip({"px": ak.Array([[], [], []])})
    records = RecordArray(array)

    assert records.shape == (3, 0)


def test_record_array_dtype():
    array = ak.zip({"px": [[1, 2, 3], [1, 2], [1]]})
    records = RecordArray(array)

    assert records.dtype == {"px": "int64"}

    array = ak.zip({"px": ak.Array([[], [], []])})
    records = RecordArray(array)

    assert records.dtype == {"px": "unknown"}


def test_vector_array_init():
    array = {
        "px": [[1, 2, 3], [1, 2], [1]],
        "py": [[1, 2, 3], [1, 2], [1]],
        "pz": [[1, 2, 3], [1, 2], [1]],
        "E": [[1, 2, 3], [1, 2], [1]],
    }
    _ = VectorArray(array)

    array = ak.zip(
        {
            "px": [[1, 2, 3], [1, 2], [1]],
            "py": [[1, 2, 3], [1, 2], [1]],
            "pz": [[1, 2, 3], [1, 2], [1]],
            "E": [[1, 2, 3], [1, 2], [1]],
        }
    )
    _ = VectorArray(array)

    array = ak.zip(
        {
            "px": [[], [], []],
            "py": [[], [], []],
            "pz": [[], [], []],
            "E": [[], [], []],
        },
    )
    _ = VectorArray(array)

    with pytest.raises(ValueError):
        VectorArray(ak.Array([[1, 2, 3], [1, 2], [1]]))


def test_vector_array_getitem():
    array = ak.zip(
        {
            "px": [[1, 2, 3], [1, 2], [1]],
            "py": [[1, 2, 3], [1, 2], [1]],
            "pz": [[1, 2, 3], [1, 2], [1]],
            "E": [[1, 2, 3], [1, 2], [1]],
        }
    )
    vectors = VectorArray(array)
    vectors = vectors["px"]

    assert isinstance(vectors, NumberArray)

    array = ak.zip(
        {
            "px": [[1, 2, 3], [1, 2], [1]],
            "py": [[1, 2, 3], [1, 2], [1]],
            "pz": [[1, 2, 3], [1, 2], [1]],
            "E": [[1, 2, 3], [1, 2], [1]],
        }
    )
    vectors = VectorArray(array)
    vectors = vectors["pt"]

    assert isinstance(vectors, NumberArray)
