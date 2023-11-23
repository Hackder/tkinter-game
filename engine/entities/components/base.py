from __future__ import annotations
from abc import ABC

from engine.models import FrameContext, Position, Size

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from engine.entities.basic import Entity


class Component(ABC):
    def create(self, entity: Entity):
        pass

    def destroy(self, entity: Entity):
        pass

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        pass

    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        pass
