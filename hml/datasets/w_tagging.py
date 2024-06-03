from pathlib import Path

import awkward as ak
import numba as nb
import numpy as np
from keras import utils
from keras.src.backend import config

from ..operations.awkward_ops import ak_from_h5, ak_to_h5


@nb.njit
def append_particles(builder, particles):
    builder.begin_list()
    for particle in particles:
        builder.begin_list()
        for property in particle:
            builder.append(property)
        builder.end_list()

    builder.end_list()


def extract_data(path):
    with open(path) as f:
        lines = f.readlines()

    particles_builder = ak.ArrayBuilder()
    progress_bar = utils.Progbar(len(lines))

    for line in lines:
        values = line.split()
        values = np.array(values, dtype=float).reshape(-1, 7)
        append_particles(particles_builder, values)

        progress_bar.add(1)

    particles = particles_builder.snapshot()

    return particles


def load_dataset(path="w_tagging"):
    """Load the w-tagging dataset from Zenodo.

    This dataset is from [Supervised jet clustering reference data](https://zenodo.org/record/3981290).

    Parameters
    ----------
    path : str, optional
        The path to the dataset directory (relative to `~/.keras/datasets`), by default "w_tagging".

    Returns
    -------
    events : ak.Array
        The events stored in an awkward array.
    labels : ak.Array
        The labels stored in an awkward array.
    """
    path = Path(config.keras_home()) / "datasets" / path
    path.mkdir(exist_ok=True, parents=True)

    qstar_path = utils.get_file(
        fname=path.name + "/qstar.txt",
        origin="https://zenodo.org/records/3981290/files/qstar.txt",
        file_hash="41829c855e1042fb335c790ef6ab72a7",
    )

    wboson_path = utils.get_file(
        fname=path.name + "/wboson.txt",
        origin="https://zenodo.org/records/3981290/files/wboson.txt",
        file_hash="c7dd129af8cc4c22e87972c57268fcb3",
    )

    if (path / "qstar.h5").exists():
        qstar_events = ak_from_h5(path / "qstar.h5")
    else:
        qstar_events = extract_data(qstar_path)
        ak_to_h5(qstar_events, path / "qstar.h5")

    if (path / "wboson.h5").exists():
        wboson_events = ak_from_h5(path / "wboson.h5")
    else:
        wboson_events = extract_data(wboson_path)
        ak_to_h5(wboson_events, path / "wboson.h5")

    events = ak.concatenate([qstar_events, wboson_events])
    labels = np.array([0] * len(qstar_events) + [1] * len(wboson_events))

    x = ak.to_regular(events, axis=-1)
    y = ak.from_numpy(labels)

    return x, y
