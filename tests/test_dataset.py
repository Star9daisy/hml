from pathlib import Path

import numpy as np

from hml.datasets import Dataset


def test_save_and_load():
    np.random.seed(42)

    dataset = Dataset(
        data=np.random.random((100, 5)),
        target=np.random.randint(0, 2, (100, 1)),
        feature_names=["a", "b", "c", "d", "e"],
        target_names={0: "background", 1: "signal"},
        description="""This is a demo dataset.

    It is used to demonstrate the functionality of the HML package.
    """,
        dataset_dir="./tests/data/demo_dataset",
    )

    dataset.save(exist_ok=True)

    files = list(Path("./tests/data/demo_dataset").iterdir())
    assert len(files) == 2
    assert Path("./tests/data/demo_dataset/dataset.npz").exists()
    assert Path("./tests/data/demo_dataset/metadata.yml").exists()

    loaded_dataset = Dataset.load("./tests/data/demo_dataset")

    assert np.all(dataset.data == loaded_dataset.data)
    assert np.all(dataset.target == loaded_dataset.target)
    assert dataset.feature_names == loaded_dataset.feature_names
    assert dataset.target_names == loaded_dataset.target_names
    assert dataset.description == loaded_dataset.description
    assert dataset.dataset_dir == loaded_dataset.dataset_dir
