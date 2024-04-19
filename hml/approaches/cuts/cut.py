import re

import awkward as ak

from hml.observables import parse


class Cut:
    def __init__(self, expression) -> None:
        self._expression = expression
        self._parse_expression(expression)

    def _parse_expression(self, expression):
        expr = expression.strip()

        self._is_veto = False
        if expr.startswith("veto"):
            self._is_veto = True
            expr = expr.replace("veto", "").strip()

        self._is_any = False
        if expr.startswith("any"):
            self._is_any = True
            expr = expr.replace("any", "").strip()

        expr = expr.replace("and", "&").replace("or", "|")

        # Split the expression by logical operators "and" and "or"
        cuts = expr.split("&")
        cuts = [cut.strip().split("|") for cut in cuts]
        cuts = [c.strip() for cut in cuts for c in cut]
        cuts = [cut.replace("(", "").replace(")", "") for cut in cuts]

        obs_pattern = r"\b(?!\d+\b)(?!\d*\.\d+\b)\S+\b"
        cuts_dict = {}
        for cut in cuts:
            obs = re.findall(obs_pattern, cut)[0]
            if "" not in cut.split(obs):
                new_cut = [cut.split(obs)[0] + obs, obs + cut.split(obs)[1]]
                cuts_dict[new_cut[0]] = obs
                cuts_dict[new_cut[1]] = obs
                expr = expr.replace(cut, f"({new_cut[0]} & {new_cut[1]})")
            else:
                cuts_dict[cut] = obs

        self._cuts_dict = cuts_dict
        self._observables_dict = {obs: parse(obs) for obs in cuts_dict.values()}
        self._expr = expr

    def read(self, events):
        for obs in self._observables_dict.values():
            obs.read(events)
        observables_dict = self._observables_dict

        cuts_results = {}
        for cut, obs in self._cuts_dict.items():
            result = eval(cut.replace(obs, f"observables_dict['{obs}'].value"))
            cuts_results[cut] = result

        # Validate the type
        shapes = set([obs.shape for obs in observables_dict.values()])
        if len(shapes) != 1:
            raise ValueError

        expression = self._expr
        for cut in cuts_results:
            cut_pattern = r"\b" + cut.replace(".", "\.") + r"\b"
            expression = re.sub(cut_pattern, f"cuts_results['{cut}']", expression)

        self._value = ak.fill_none(eval(expression), False)

        if self._value.ndim > 1:
            if self._is_any:
                self._value = ak.any(self._value, axis=1)
            else:
                self._value = ak.all(self._value, axis=1)

        if self._is_veto:
            self._value = ~self._value

        return self

    @property
    def value(self):
        return self._value

    @property
    def expression(self):
        return self._expression
