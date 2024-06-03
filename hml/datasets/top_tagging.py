from pathlib import Path

import awkward as ak
import numpy as np
import pandas as pd
from keras import utils
from keras.src.backend import config


def load_dataset(path="top_tagging"):
    """Load the top-tagging dataset from Zenodo.

    This dataset is from [Top Quark Tagging Reference Dataset](https://zenodo.org/records/2603256).

    Parameters
    ----------
    path : str, optional
        The path to the dataset directory (relative to `~/.keras/datasets`), by default "top_tagging".

    Returns
    -------
    events : ak.Array
        The events stored in an awkward array.
    labels : ak.Array
        The labels stored in an awkward array.
    """
    path = Path(config.keras_home()) / "datasets" / path
    path.mkdir(exist_ok=True, parents=True)

    train_path = utils.get_file(
        fname=path.name + "/train.h5",
        origin="https://zenodo.org/record/2603256/files/train.h5",
        file_hash="45663819f47c13724f67eb0fd80bfa5c",
    )

    test_path = utils.get_file(
        fname=path.name + "/test.h5",
        origin="https://zenodo.org/record/2603256/files/test.h5",
        file_hash="13163479dee30a5fe546e4536cc3d04d",
    )

    val_path = utils.get_file(
        fname=path.name + "/val.h5",
        origin="https://zenodo.org/record/2603256/files/val.h5",
        file_hash="dca4b7248027618f041f9baa86d360fc",
    )

    df_train = pd.read_hdf(train_path, key="table")
    df_test = pd.read_hdf(test_path, key="table")
    df_val = pd.read_hdf(val_path, key="table")

    x_train = df_train.iloc[:, :800].values.reshape(-1, 200, 4)
    y_train = df_train.iloc[:, -1].values

    x_test = df_test.iloc[:, :800].values.reshape(-1, 200, 4)
    y_test = df_test.iloc[:, -1].values

    x_val = df_val.iloc[:, :800].values.reshape(-1, 200, 4)
    y_val = df_val.iloc[:, -1].values

    x = np.concatenate([x_train, x_test, x_val])
    y = np.concatenate([y_train, y_test, y_val])

    x = ak.from_numpy(x)
    y = ak.from_numpy(y)

    return x, y
