from ..registration import register
from .physics_object import PhysicsObjectBase


class Photon(PhysicsObjectBase): ...


register(Photon, "Photon", existing_ok=True)
register(Photon, "photon", existing_ok=True)
