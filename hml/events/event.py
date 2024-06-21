from ..types import Event


class EventBase(Event):
    """Base class for dict-like events.

    Events store the data as an awkward record array.
    """
