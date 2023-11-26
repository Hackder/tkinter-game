from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING, Any

from engine.models import FrameContext
from engine.threed.models import Position3d, Quaternion, Size3d

if TYPE_CHECKING:
    from engine.threed.entities.basic import Entity3d


class Component3d:
    def create(self, entity: Entity3d):
        pass

    def destroy(self, entity: Entity3d):
        pass

    def before_paint(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
    ):
        pass
