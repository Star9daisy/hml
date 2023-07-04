from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from numpy import ndarray
from sklearn.ensemble import GradientBoostingClassifier


class BoostedDecisionTree:
    def __init__(
        self,
        name: str = "boosted_decision_tree",
        learning_rate: float = 0.1,
        n_estimators: int = 100,
        **kwargs,
    ):
        self._name = name
        self.model = GradientBoostingClassifier(
            learning_rate=learning_rate, n_estimators=n_estimators, **kwargs
        )
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators

    @property
    def name(self) -> str:
        return self._name

    @property
    def n_parameters(self) -> int:
        max_nodes_per_tree = 2 ** (self.model.max_depth + 1) - 1
        max_parameters = max_nodes_per_tree * self.model.n_estimators
        return max_parameters

    def compile(
        self,
        optimizer: None = None,
        loss: str = "log_loss",
        metrics: None = None,
    ):
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics
        self.model.set_params(loss=loss)

    def fit(self, x: Any, y: Any, verbose: int = 1, *args, **kwargs) -> None:
        self.model.set_params(verbose=verbose, *args, **kwargs)
        self.model.fit(x, y)

    def predict(self, x: Any) -> ndarray:
        return self.model.predict_proba(x)

    def summary(self) -> str:
        output = ["Model: {}".format(self.name)]
        for parameter, value in self.model.get_params(deep=False).items():
            output.append(f"- {parameter}: {value}")
        return "\n".join(output)

    def save(self, file_path: str | Path, overwrite: bool = True) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.suffix != ".pkl":
            file_path = file_path.with_suffix(".pkl")

        if file_path.exists() and not overwrite:
            raise FileExistsError(f"Checkpoint {file_path} already exists.")

        with open(file_path, "wb") as f:
            pickle.dump(self.model, f)

    @classmethod
    def load(cls, file_path: str | Path, *args, **kwargs) -> BoostedDecisionTree:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Checkpoint {file_path} does not exist.")

        with open(file_path, "rb") as f:
            model = pickle.load(f, *args, **kwargs)
            return cls(model=model)
