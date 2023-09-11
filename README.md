# HEP ML Lab (HML)
[![PyPI - Version](https://img.shields.io/pypi/v/hep-ml-lab)](https://pypi.org/project/hep-ml-lab/)
[![Downloads](https://static.pepy.tech/badge/hep-ml-lab)](https://pepy.tech/project/hep-ml-lab)
[![codecov](https://codecov.io/gh/Star9daisy/hep-ml-lab/branch/main/graph/badge.svg?token=6VWJi5ct6c)](https://app.codecov.io/gh/Star9daisy/hep-ml-lab)
[![GitHub](https://img.shields.io/github/license/star9daisy/hep-ml-lab)](https://github.com/Star9daisy/hep-ml-lab/blob/main/LICENSE)


❗ Before the official version is released, please note that the program may
have significant differences as versions change.

## Introduction
HEP-ML-Lab is an end-to-end framework used for research combining high-energy
physics phenomenology with machine learning. It covers three main parts: the
generation of simulated data, the conversion of data representation, and the
application of analysis methods.

With HML, researchers can easily compare the performance between traditional
methods and modern machine learning, and obtain robust and reproducible results.

To get started, please check out the [documents](https://star9daisy.github.io/hep-ml-lab/).

## Installation
```python
pip install hep-ml-lab
```

## Module overview
- `hml.generators`: API of Madgraph5 for simulating colliding events;
- `hml.theories`: Particle physics models;
- `hml.observables`: General observables in jet physics;
- `hml.representations`: Different data structure used to represent an event;
- `hml.datasets`: Existing datasets and helper classes for creating new datasets;
- `hml.methods`: Cuts, trees and networks for classification;
- `hml.metrics`: Metrics used in classical signal vs background analysis;

## Updates

### v0.2.2
- Change output structure of `hml.generators.Madgraph5` to ensure reproducibility.
- Refactor `hml.generators.Madgraph5` and `hml.generators.MG5Run` to make
  them more robust.
### v0.2.1
- Add `summary` to `hml.generators.Madgraph5` to print a summary of all run.
- Add `remove` to `hml.generators.Madgraph5` to remove a run.
- Add `clean` to `hml.generators.Madgraph5` to remove the output directory.