from typing import Any
from engine.entities.basic import Entity
from engine.entities.components.base import Component
from engine.entities.types import BoundValue
from engine.models import FrameContext, Position, Size


class Translate(Component):
    def __init__(
        self,
        *,
        position: Position | None = None,
        get_position: BoundValue[Position] | None = None
    ):
        self.position = position
        self.get_position = get_position

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        if self.get_position is not None:
            position.mut_add(self.get_position())
        elif self.position is not None:
            position.mut_add(self.position)
