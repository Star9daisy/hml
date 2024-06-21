import re

from typeguard import typechecked

from ..types import IndexLike


@typechecked
def index_to_str(index: IndexLike) -> str:
    """Converts an index-like object to a string.

    Parameters
    ----------
    index : IndexLike
        The index-like object to convert.

    Returns
    -------
    str
        The string representation of the index-like object.

    Examples
    --------
    >>> index_to_str(0)
    '0'
    >>> index_to_str(slice(1, 2))
    '1:2'
    >>> index_to_str(slice(1, None))
    '1:'
    >>> index_to_str(slice(None, 2))
    ':2'
    >>> index_to_str(slice(None, None))
    ''
    """

    if isinstance(index, int):
        return str(index)

    elif isinstance(index, slice):
        start = index.start
        stop = index.stop

        if start is None:
            start = ""

        if stop is None:
            stop = ""

        if start == stop == "":
            return ""
        else:
            return f"{start}:{stop}"


@typechecked
def str_to_index(string: str) -> IndexLike:
    """Converts a string to an index-like object.

    Parameters
    ----------
    string : str
        The string to convert.

    Returns
    -------
    IndexLike
        The index-like object.

    Examples
    --------
    >>> str_to_index("0")
    0
    >>> str_to_index("1:2")
    slice(1, 2, None)
    >>> str_to_index("1:")
    slice(1, None, None)
    >>> str_to_index(":2")
    slice(None, 2, None)
    >>> str_to_index("")
    slice(None, None, None)
    """
    index_pattern = r"(\d+)?(:)?(\d+)?"
    start, colon, stop = re.match(index_pattern, string).groups()

    if start is not None:
        start = int(start)

    if stop is not None:
        stop = int(stop)

    if start is not None and colon is None and stop is None:
        return start
    else:
        return slice(start, stop)
