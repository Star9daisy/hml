from __future__ import annotations

import io
import re
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Literal, Union

import awkward as ak
import numpy as np

PathLike = Union[str, Path]
CutLayerTopologies = Literal["parallel", "sequential"]


class Generator:
    ...


class Observable(ABC):
    ALL_OBSERVABLES = {}

    def __init__(self, physics_object: str | None = None, name: str | None = None):
        self.physics_object = physics_object
        if self.physics_object is not None:
            self.objs = self.parse_physics_object(self.physics_object)
        else:
            self.objs = []

        self._name = self.__class__.__name__ if name is None else name
        self._value = None

    def read(self, event):
        self.main_objs = []
        self.sub_objs = []
        self.event = event

        if self.physics_object:
            for obj in self.objs:
                main_name = obj["main"][0]
                main_start = obj["main"][1]
                main_end = obj["main"][2]

                main_objs = list(getattr(event, main_name))
                clipped_main_objs = main_objs[slice(main_start, main_end)]
                required_main_length = (
                    main_end - main_start if main_end is not None else None
                )
                actual_main_length = len(clipped_main_objs)

                if (
                    required_main_length is not None
                    and required_main_length > actual_main_length
                ):
                    main_padding_length = main_end - main_start - len(clipped_main_objs)
                    padded_main_objs = clipped_main_objs + [None] * main_padding_length
                    prepared_main_objs = padded_main_objs
                else:
                    prepared_main_objs = clipped_main_objs
                self.main_objs.append(prepared_main_objs)

                if obj.get("sub") is None:
                    self.sub_objs.append([])
                    continue

                sub_name = obj["sub"][0]
                sub_start = obj["sub"][1]
                sub_end = obj["sub"][2]

                sub_objs_per_main = []
                for main_obj in prepared_main_objs:
                    if main_obj is None:
                        if sub_end is None:
                            sub_objs_per_main.append([None])
                        else:
                            sub_objs_per_main.append([None] * required_sub_length)
                        continue

                    sub_objs = list(getattr(main_obj, sub_name))
                    clipped_sub_objs = sub_objs[slice(sub_start, sub_end)]
                    required_sub_length = (
                        sub_end - sub_start if sub_end is not None else None
                    )
                    acutal_sub_length = len(clipped_sub_objs)

                    if (
                        required_sub_length is not None
                        and required_sub_length > acutal_sub_length
                    ):
                        sub_padding_length = required_sub_length - acutal_sub_length
                        padded_sub_objs = clipped_sub_objs + [None] * sub_padding_length
                        prepared_sub_objs = padded_sub_objs
                    else:
                        prepared_sub_objs = clipped_sub_objs
                    sub_objs_per_main.append(prepared_sub_objs)

                self.sub_objs.append(sub_objs_per_main)

        self._value = self.get_value()

        return self

    @property
    def name(self):
        if self.physics_object:
            return f"{self.physics_object}.{self._name}"
        else:
            return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def shape(self):
        captured_output = io.StringIO()
        self.to_awkward().type.show(captured_output)
        return captured_output.getvalue().strip()

    def to_awkward(self, dtype=None):
        ak_array = ak.from_iter(self.value)
        ak_array = ak.values_astype(ak_array, dtype)
        try:
            ak_array = ak.to_regular(ak_array)
        except ValueError:
            pass
        return ak_array

    def to_numpy(self, keepdims=None, dtype=None):
        if keepdims is not None:
            return np.array(self._value, dtype=dtype)
        else:
            return np.squeeze(np.array(self._value, dtype=dtype))

    @abstractmethod
    def get_value(self) -> Any:
        ...

    def parse_branch(self, branch: str):
        if re.match(r"^([A-Za-z]+)$", branch):
            branch += ":"

        if match := re.match(r"^([A-Za-z]+)(\d+)$", branch):
            obj, index = match.groups()
            start = int(index)
            stop = start + 1
        elif match := re.match(r"^([A-Za-z]+)(\d*:?\d*)$", branch):
            obj, agnostic_index = match.groups()
            indices = agnostic_index.split(":")
            if indices[0] == "" and indices[1] == "":
                start = 0
                stop = None
            elif indices[0] == "" and indices[1] != "":
                start = 0
                stop = int(indices[1])
            elif indices[0] != "" and indices[1] == "":
                start = int(indices[0])
                stop = None
            else:
                start = int(indices[0])
                stop = int(indices[1])
        else:
            return

        return obj, start, stop

    def parse_physics_object(self, physics_object: str):
        output = []
        for phyobj_name in physics_object.split(","):
            item = {}

            if "." not in phyobj_name:
                item["main"] = self.parse_branch(phyobj_name)
                output.append(item)
            else:
                main, sub = phyobj_name.split(".")
                item["main"] = self.parse_branch(main)
                item["sub"] = self.parse_branch(sub)
                output.append(item)
        return output

    def __repr__(self) -> str:
        return f"{self.name}: {self.value}"

    def __eq__(self, other: Observable) -> bool:
        return self.name == other.name

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        Observable.ALL_OBSERVABLES[cls.__name__] = cls

    @classmethod
    def add_alias(cls, *alias: str) -> None:
        """Add alias for the class name."""
        for i in alias:
            Observable.ALL_OBSERVABLES[i] = cls


class Representation:
    ...


class Dataset:
    ...


class Approach:
    ...


class Metric:
    ...
