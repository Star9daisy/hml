import numpy as np
from keras import ops

from hml.operations import keras_ops as kro


def test_histogram_fixed_width():
    values = ops.array([1.0, 2.0, 3.0, 4.0, 5.0])
    value_range = (1.0, 5.0)
    nbins = 5
    expected_output = ops.array([1, 1, 1, 1, 1], dtype="int32")

    output = kro.histogram_fixed_width(values, value_range, nbins)
    np.testing.assert_array_equal(output, expected_output)

    values = ops.array([1.0, 2.0, 2.5, 3.0, 4.0, 5.0])
    value_range = (1.0, 5.0)
    nbins = 4
    expected_output = ops.array([1, 2, 1, 2], dtype="int32")

    output = kro.histogram_fixed_width(values, value_range, nbins)
    np.testing.assert_array_equal(output, expected_output)


def test_unique():
    tensor = ops.array([1, 2, 2, 3, 4, 4, 4, 5])
    expected_output = ops.array([1, 2, 3, 4, 5])

    output = kro.unique(tensor)
    np.testing.assert_array_equal(output, expected_output)

    tensor = ops.array([1, 1, 1, 1])
    expected_output = ops.array([1])

    output = kro.unique(tensor)
    np.testing.assert_array_equal(output, expected_output)

    tensor = ops.array([3, 1, 2, 2, 1])
    expected_output = ops.array([1, 2, 3])

    output = kro.unique(tensor)
    np.testing.assert_array_equal(output, expected_output)

    tensor = ops.array([])
    expected_output = ops.array([])

    output = kro.unique(tensor)
    np.testing.assert_array_equal(kro.unique(tensor), expected_output)
