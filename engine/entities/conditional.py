import copy
from tkinter import Canvas
from typing import Any, Callable
from engine.entities.basic import Entity
from engine.entities.components.base import Component
from engine.entities.state import EntityState
from engine.entities.types import BoundValue
from engine.models import Constraints, FrameContext, Position, Size


class EntitySwitchState(EntityState):
    def __init__(self, current: BoundValue[Any]):
        self._bound_current = current
        self.current = current()

    def copy(self):
        return copy.copy(self)


class EntitySwitch(Entity):
    state: EntitySwitchState

    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        components: list[Component] = [],
        current: BoundValue[Any],
        entities: dict[Any, Callable[[], Entity]],
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.state = EntitySwitchState(current=current)
        self._state = self.state.copy()
        self.entities = entities
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        self.current = self.entities[self.state.current]()
        self.current.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)

        self.current.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        for component in self.components:
            component.before_paint(self, ctx, position, self._size, self._state)

        self.current.paint(ctx, position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        changed = self.state.update()
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        if "current" in changed:
            self.current.destroy()
            self.current = self.entities[self.state.current]()
            self.current.create(self.canvas)

        self._state = state

        child_size = self.current.layout(ctx, constraints)
        self.current._size = child_size

        return child_size
