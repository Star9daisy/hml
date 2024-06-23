from hml.operations import fastjet_ops as fjo


def test_get_algorithm():
    assert fjo.get_algorithm("kt") == 0
    assert fjo.get_algorithm("ca") == 1
    assert fjo.get_algorithm("ak") == 2
    assert fjo.get_algorithm("undefined") == 999
    assert fjo.get_algorithm("unknown") == 999
