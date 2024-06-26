from ..registration import register
from .physics_object import PhysicsObjectBase


class Muon(PhysicsObjectBase): ...


register(Muon, "Muon", existing_ok=True)
register(Muon, "muon", existing_ok=True)
