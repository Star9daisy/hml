# HEP ML Lab (HML)
[![PyPI - Version](https://img.shields.io/pypi/v/hep-ml-lab)](https://pypi.org/project/hep-ml-lab/)
[![Downloads](https://static.pepy.tech/badge/hep-ml-lab)](https://pepy.tech/project/hep-ml-lab)
[![codecov](https://codecov.io/gh/Star9daisy/hep-ml-lab/branch/main/graph/badge.svg?token=6VWJi5ct6c)](https://app.codecov.io/gh/Star9daisy/hep-ml-lab)
[![GitHub](https://img.shields.io/github/license/star9daisy/hep-ml-lab)](https://github.com/Star9daisy/hep-ml-lab/blob/main/LICENSE)

## Introduction
HEP-ML-Lab is an end-to-end framework used for research combining high-energy
physics phenomenology with machine learning. It covers three main parts: the
generation of simulated data, the conversion of data representation, and the
application of analysis approaches.

With HML, researchers can easily compare the performance between traditional
methods and modern machine learning algorithms, and obtain robust and
reproducible results.

To get started, please check out the [documents](https://star9daisy.github.io/hep-ml-lab/).

## Installation
```python
pip install hep-ml-lab
```

Check out the [install via pip](install/pip.md) for more details of prerequisites and post-installation steps or [install via Docker](install/docker.md) for a hassle-free experience.

## Module overview

![module_overview](images/hml_modules.png)

- `hml.generators`: API of Madgraph5 for simulating colliding events;
- `hml.physics_objects`: General physics objects;
- `hml.observables`: General observables in jet physics;
- `hml.representations`: Different data structure used to represent an event;
- `hml.datasets`: Existing datasets and helper classes for creating new datasets;
- `hml.approaches`: Cuts, trees and networks for classification;
- `hml.metrics`: Metrics used in classical signal vs background analysis;
