from typing import Literal

import awkward as ak
import vector
from typeguard import typechecked

from ..types import AwkwardArray, Self

vector.register_awkward()


@typechecked
def convert_to_regular_array(array: AwkwardArray) -> AwkwardArray:
    typestr = array.typestr
    shape = typestr.split(" * ")[:-1]

    for axis_i in range(array.ndim):
        if shape[axis_i].isdigit():
            continue

        try:
            array = ak.to_regular(array, axis=axis_i)
        except Exception:
            pass

    return array


@typechecked
def create_nested_list(level: int) -> list:
    if level == 0:
        return [None]
    else:
        return [create_nested_list(level - 1)]


@typechecked
def pad_none_keeping_structure(
    array: AwkwardArray,
    target: int,
    axis: int = 1,
) -> AwkwardArray:
    axis = axis if axis >= 0 else array.ndim + axis
    n_elements = ak.num(array, axis)
    n_elements = n_elements if axis > 0 else ak.from_iter([n_elements])

    if ak.all(target <= n_elements):
        index = [slice(None)] * axis + [slice(target)] + [...]
        sliced = array[tuple(index)]
        return sliced

    if array.ndim - 2 - axis >= 0:
        return ak.fill_none(
            ak.pad_none(array, target, axis=axis, clip=True),
            create_nested_list(array.ndim - 2 - axis),
            axis=axis,
        )
    else:
        return ak.pad_none(array, target, axis=axis, clip=True)


def pad_none_according_to_indices(
    array: AwkwardArray,
    indices: tuple[int | slice, ...],
) -> AwkwardArray:
    for i, index_i in enumerate(indices):
        if isinstance(index_i, int):
            array = pad_none_keeping_structure(array, index_i + 1, axis=i)
        elif index_i.stop is not None:
            array = pad_none_keeping_structure(array, index_i.stop, axis=i)

    return array


@typechecked
def convert_to_array(object: list | dict | AwkwardArray) -> AwkwardArray:
    if isinstance(object, list):
        return ak.Array(object)
    elif isinstance(object, dict):
        return ak.zip(object)
    elif "option" in object.typestr:
        return ak.from_iter(object)
    else:
        return object


@typechecked
class NumberArray:
    def __init__(self, object: list | AwkwardArray) -> None:
        array = convert_to_array(object)
        if len(array.fields) != 0:
            raise ValueError("NumberArray requires the input array has no fields")

        self.array = convert_to_regular_array(array)

    def __repr__(self) -> str:
        html_repr = self.array._repr_mimebundle_()["text/html"]
        text_repr = html_repr.replace("<pre>", "").replace("</pre>", "")

        return text_repr

    def __getitem__(self, index: int | slice | tuple[int | slice, ...]) -> Self:
        indices = index if isinstance(index, tuple) else (index,)
        padded = pad_none_according_to_indices(self.array, indices)
        indexed = padded[tuple(indices)]

        return NumberArray(indexed)

    @property
    def shape(self) -> tuple[int | Literal["var"], ...]:
        shape = self.array.typestr.split(" * ")[:-1]
        shape = tuple(int(s) if s.isdigit() else "var" for s in shape)

        return shape

    @property
    def dtype(self) -> str:
        dtype = str(self.array.layout.form.column_types()[0])
        dtype = dtype if dtype != "empty" else "unknown"

        return dtype


@typechecked
class RecordArray:
    def __init__(self, object: dict | AwkwardArray) -> None:
        array = convert_to_array(object)
        if len(array.fields) == 0:
            raise ValueError("RecordArray requires the input array has fields")

        self.array = convert_to_regular_array(array)

    def __repr__(self) -> str:
        html_repr = self.array._repr_mimebundle_()["text/html"]
        text_repr = html_repr.replace("<pre>", "").replace("</pre>", "")

        return text_repr

    def __getitem__(
        self, key: str | int | slice | tuple[str | int | slice, ...]
    ) -> Self | NumberArray:
        if isinstance(key, str):
            try:
                array = self.array[key]
            except Exception:
                array = getattr(self.array, key)
        else:
            indices = key if isinstance(key, tuple) else (key,)
            padded = pad_none_according_to_indices(self.array, indices)
            array = padded[tuple(indices)]

        if len(array.fields) == 0:
            return NumberArray(array)
        else:
            return RecordArray(array)

    @property
    def shape(self) -> tuple[int | Literal["var"], ...]:
        shape = self.array.typestr.split(" * ")[:-1]
        shape = tuple(int(s) if s.isdigit() else "var" for s in shape)

        return shape

    @property
    def dtype(self) -> dict[str, str]:
        columns = self.array.layout.form.columns()
        types = self.array.layout.form.column_types()

        dtype = {}
        for field, type_ in zip(columns, types):
            dtype[field] = str(type_) if type_ != "empty" else "unknown"

        return dtype


@typechecked
class VectorArray(RecordArray):
    def __init__(self, object: dict | ak.Array):
        super().__init__(object)
        self.array = ak.with_name(self.array, "Momentum4D")
