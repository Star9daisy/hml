from pathlib import Path
from typing import Union

import awkward as ak
import keras
import numpy as np

Number = int | float
IndexLike = int | slice
PathLike = Path | str
ArrayLike = np.ndarray | ak.Array


tensor_types = ()

try:
    import tensorflow as tf

    tensor_types += (tf.Tensor,)
except ImportError:
    pass

try:
    import torch

    tensor_types += (torch.Tensor,)
except ImportError:
    pass

try:
    import jax

    tensor_types += (jax.numpy.ndarray,)
except ImportError:
    pass

NumericTensor = Union[tensor_types]
SymbolicTensor = keras.KerasTensor
Tensor = NumericTensor | SymbolicTensor
