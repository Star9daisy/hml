from hml.naming import index_to_str, str_to_index


def test_index_to_str():
    assert index_to_str(0) == "0"
    assert index_to_str(slice(1, 2)) == "1:2"
    assert index_to_str(slice(1, None)) == "1:"
    assert index_to_str(slice(None, 2)) == ":2"
    assert index_to_str(slice(None, None)) == ""


def test_str_to_index():
    assert str_to_index("0") == 0
    assert str_to_index("1:2") == slice(1, 2)
    assert str_to_index("1:") == slice(1, None)
    assert str_to_index(":2") == slice(None, 2)
    assert str_to_index("") == slice(None, None)
