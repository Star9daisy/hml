from ..registration import register
from .physics_object import PhysicsObjectBase


class Electron(PhysicsObjectBase): ...


register(Electron, "Electron", existing_ok=True)
register(Electron, "electron", existing_ok=True)
