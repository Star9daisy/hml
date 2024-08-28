from typeguard import typechecked

from hml.saving.registration import registered_object


@typechecked
@registered_object(name="tau(?P<m>\d)(?P<n>\d)")
class NSubjettiness:
    def __init__(self, m: int, n: int, name: str | None = None) -> None:
        self.m = m
        self.n = n
        self._name = name

    @property
    def name(self) -> str:
        if self._name:
            return self._name

        return f"tau{self.m}{self.n}"

    @property
    def config(self) -> dict:
        return {"m": self.m, "n": self.n, "name": self._name}

    @classmethod
    def from_config(cls, config: dict) -> "NSubjettiness":
        m = int(config["m"])
        n = int(config["n"])
        name = config.get("name")
        return cls(m=m, n=n, name=name)
