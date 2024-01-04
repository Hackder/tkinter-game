import math
import copy
from tkinter import Canvas
from typing import Any

from engine.animation.utils import Animation, AnimationDirection, AnimationEnd
from engine.entities.basic import Entity
from engine.entities.components.base import Component
from engine.models import Size, Position, FrameContext, Constraints, Color
from engine.threed.entities.basic import Entity3d
from engine.threed.entities.components.base import Component3d
from engine.threed.models import Camera, Position3d, Size3d, Quaternion


class PaddingEffect(Component):
    def __init__(
        self, *, start: float, end: float, duration: float, repeat_times: int = 0
    ):
        self.start = start
        self.end = end
        self.anim = Animation(
            duration=duration,
            direction=AnimationDirection.Alternate,
            repeat_times=repeat_times,
            end=AnimationEnd.End,
        )

    def before_layout(self, entity, ctx, state):
        if state is None or not hasattr(state, "padding"):
            raise Exception(
                "PaddingEffect component must be on an entity which supports padding"
            )

        value = self.anim.process(ctx.delta_time)

        state.padding.left += value * (self.end - self.start) + self.start
        state.padding.right += value * (self.end - self.start) + self.start
        state.padding.top += value * (self.end - self.start) + self.start
        state.padding.bottom += value * (self.end - self.start) + self.start

        if self.anim.done:
            entity.components.remove(self)
            entity.state.padding.left += value * (self.end - self.start) + self.start  # type: ignore
            entity.state.padding.right += value * (self.end - self.start) + self.start  # type: ignore
            entity.state.padding.top += value * (self.end - self.start) + self.start  # type: ignore
            entity.state.padding.bottom += value * (self.end - self.start) + self.start  # type: ignore


class ChangeSize(Component):
    def create(self, entity):
        self.entity = entity
        entity.canvas.tag_bind(entity.id, "<Button-1>", self.click, add="+")

    def click(self, e):
        if self.entity.state.size.width == 200:
            self.entity.state.size.width = 100
        else:
            self.entity.state.size.width = 200


class ChangePosition(Component3d):
    def create(self, entity):
        self.entity = entity
        for id in entity.ids:
            entity.canvas.tag_bind(id, "<Button-1>", self.click, add="+")

    def destroy(self, entity):
        for id in entity.ids:
            entity.canvas.tag_unbind(id, "<Button-1>")

    def click(self, e):
        if self.entity.state.position.x == 100:
            self.entity.state.position.x = 0
        else:
            self.entity.state.position.x = 100


class ChangeRotation(Component3d):
    def create(self, entity):
        self.entity = entity
        for id in entity.ids:
            entity.canvas.tag_bind(id, "<Button-1>", self.click, add="+")

    def destroy(self, entity):
        for id in entity.ids:
            entity.canvas.tag_unbind(id, "<Button-1>")

    def click(self, e):
        if self.entity.state.rotation == Quaternion.identity():
            self.entity.state.rotation = Quaternion.from_axis_angle(
                axis=Position3d(x=1, y=1, z=0), angle=math.pi
            )
        else:
            self.entity.state.rotation = Quaternion.identity()


class ChangeColor(Component):
    def create(self, entity):
        self.entity = entity
        entity.canvas.tag_bind(entity.id, "<Button-1>", self.click, add="+")

    def click(self, e):
        if self.entity.state.fill == Color.yellow():
            self.entity.state.fill = Color.gray()
        else:
            self.entity.state.fill = Color.yellow()


class EntitySwitcherState:
    def __init__(self, current: int = 0):
        self.current = current

    def copy(self):
        return copy.copy(self)


class EntitySwitcher(Entity):
    state: EntitySwitcherState

    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        current: int = 0,
        components: list[Component] = [],
        entities: list[Entity]
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.state = EntitySwitcherState(current=current)
        self.last_curr = current
        self._state = self.state.copy()
        self.entities = entities
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas
        for component in self.components:
            component.create(self)

        self.entities[self.state.current].create(canvas)

    def destroy(self, entity: Entity):
        for component in self.components:
            component.destroy(self)

        self.entities[self.state.current].destroy(self)

    def paint(self, ctx: FrameContext, position: Position):
        for component in self.components:
            component.before_paint(self, ctx, position, self._size, self._state)

        if self._state.current != self.last_curr:
            curr = self.entities[self.state.current]
            last = self.entities[self.last_curr]
            curr.create(self.canvas)
            self.canvas.tag_raise(curr.id, last.id)
            last.destroy(self)
            self.last_curr = self.state.current

        self.entities[self._state.current].paint(ctx, position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        child_size = self.entities[state.current].layout(ctx, constraints)
        self.entities[state.current]._size = child_size

        return child_size


class Draggable(Component3d):
    def __init__(self):
        self.dragging = False
        self.drag_start = Position3d(x=0, y=0, z=0)
        self.camera = None

    def create(self, entity):
        self.entity = entity
        entity.canvas.bind("<B1-Motion>", self.drag)
        for id in entity.ids:
            entity.canvas.tag_bind(id, "<Button-1>", self.click, add="+")
            entity.canvas.tag_bind(id, "<ButtonRelease-1>", self.release, add="+")

    def before_paint(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        camera: Camera,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
    ):
        self.camera = camera

    def click(self, e):
        if self.camera is None:
            return

        self.dragging = True
        self.drag_start = self.camera.screen_to_world(
            e.x, e.y, self.entity.state.position.z
        )

    def drag(self, e):
        if self.camera is None:
            return

        world_pos = self.camera.screen_to_world(e.x, e.y, self.entity.state.position.z)

        if self.dragging:
            self.entity.state.position.x += world_pos.x - self.drag_start.x
            self.entity.state.position.y += world_pos.y - self.drag_start.y
            self.drag_start = Position3d(x=world_pos.x, y=world_pos.y, z=0)

    def release(self, e):
        self.dragging = False


class SwitchOnClick(Component):
    def create(self, entity):
        self.entity = entity
        entity.canvas.bind("<Button-1>", self.click)

    def click(self, e):
        self.entity.state.current = (self.entity.state.current + 1) % len(
            self.entity.entities
        )
