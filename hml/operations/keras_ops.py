from __future__ import annotations

import numpy as np
from keras import ops
from typeguard import typechecked

from ..types import Number, Tensor


@typechecked
def histogram_fixed_width(
    values: Tensor,
    value_range: tuple[Number, Number],
    nbins: int,
    dtype: str = "int32",
) -> Tensor:
    """Compute the histogram of a set of values using fixed-width bins."""
    value_min, value_max = value_range

    # Generate bin edges including the infinities at the boundaries
    bin_edges = ops.linspace(value_min, value_max, nbins + 1)
    inf = ops.convert_to_tensor([np.inf], dtype=values.dtype)
    bin_edges = ops.concatenate([-inf, bin_edges[1:-1], inf])

    lower = bin_edges[:-1]
    upper = bin_edges[1:]

    # Initialize histogram tensor
    histogram = ops.zeros((nbins,), dtype=dtype)

    def update_histogram(i, histogram):
        # Count the number of values in the current bin
        is_selected = ops.logical_and(lower[i] <= values, values < upper[i])
        bin_count = ops.count_nonzero(ops.where(is_selected, 1.0, 0.0))
        # Update the histogram at the i-th bin
        return ops.scatter_update(histogram, [[i]], [bin_count])

    # Loop through bins and update histogram
    return ops.fori_loop(0, nbins, update_histogram, histogram)


@typechecked
def unique(tensor: Tensor) -> Tensor:
    """Find the unique elements in a tensor."""
    # Handle the empty tensor case
    if ops.size(tensor) == 0:
        return ops.array([])

    sorted_tensor = ops.sort(tensor)

    # Detect the unique elements by checking for inequality between consecutive
    # elements
    selection = ops.not_equal(sorted_tensor[1:], sorted_tensor[:-1])
    selection_indices = ops.add(ops.squeeze(ops.where(selection), 0), 1)

    # Include the first element (index 0) in the unique indices
    unique_indices = ops.append([0], selection_indices)

    # Gather the unique elements using the unique indices
    unique_elements = ops.take(sorted_tensor, unique_indices)
    return unique_elements
