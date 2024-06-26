from ..registration import register
from .physics_object import PhysicsObjectBase


class Track(PhysicsObjectBase): ...


register(Track, "Track", existing_ok=True)
register(Track, "track", existing_ok=True)
