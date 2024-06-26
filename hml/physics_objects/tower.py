from ..registration import register
from .physics_object import PhysicsObjectBase


class Tower(PhysicsObjectBase): ...


register(Tower, "Tower", existing_ok=True)
register(Tower, "tower", existing_ok=True)
