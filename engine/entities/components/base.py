from __future__ import annotations
from abc import ABC

from engine.models import FrameContext, Position, Size

from typing import TYPE_CHECKING, Any, Callable

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


class Hook(Component):
    def __init__(
        self,
        *,
        before_paint: Callable[[Entity, FrameContext, Position, Size, Any | None], None]
        | None = None,
        before_layout: Callable[[Entity, FrameContext, Any | None], None] | None = None,
    ):
        self._before_paint = before_paint
        self._before_layout = before_layout

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        if self._before_paint is not None:
            self._before_paint(entity, ctx, position, size, state)

    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        if self._before_layout is not None:
            self._before_layout(entity, ctx, state)


class LeaveOriginal:
    pass


class Bind(Component):
    def __init__(self, property: str, getter: Callable):
        self.property = property
        self.getter = getter

    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        val = self.getter()
        if isinstance(val, LeaveOriginal):
            return

        setattr(state, self.property, val)


class PaintBind(Component):
    def __init__(self, property: str, getter: Callable):
        self.property = property
        self.getter = getter

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        val = self.getter()
        if isinstance(val, LeaveOriginal):
            return

        setattr(state, self.property, val)


class PositionGroup(Component):
    def __init__(self, components: list[Component]):
        self.components = components

    def create(self, entity: Entity):
        for component in self.components:
            component.create(entity)

    def destroy(self, entity: Entity):
        for component in self.components:
            component.destroy(entity)

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        pos = Position.zero()
        for component in self.components:
            component.before_paint(entity, ctx, pos, size, state)

        position.mut_add(pos)

    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        for component in self.components:
            component.before_layout(entity, ctx, state)
