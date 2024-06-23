from __future__ import annotations

import fastjet as fj

JET_ALGORITHMS = {
    "kt": fj.kt_algorithm,
    "ca": fj.cambridge_algorithm,
    "ak": fj.antikt_algorithm,
    "undefined": fj.undefined_jet_algorithm,
}


def get_algorithm(name: str) -> int:
    """Get a jet algorithm by its name.

    Parameters
    ----------
    name : str
        Jet algorithm name.

    Returns
    -------
    fastjet.JetAlgorithm
        Jet algorithm.

    Examples
    --------
    >>> import fastjet as fj
    >>> from hml.operations import fastjet_ops as fjo

    >>> fjo.get_algorithm("kt")
    0
    >>> fj.kt_algorithm
    0
    """
    return JET_ALGORITHMS.get(name, fj.undefined_jet_algorithm)
