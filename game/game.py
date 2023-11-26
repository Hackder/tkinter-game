import math
import copy
import os
from tkinter import Canvas
from PIL.Image import Resampling
from typing import Any
from timeit import default_timer as timer

from engine.animation.utils import Animation, AnimationDirection, AnimationEnd, Easing
from engine.assets import Asset, AssetType
from engine.entities.basic import Entity, Rect, RootScene, Text
from engine.entities.components.base import Component
from engine.entities.components.debug import (
    DebugBounds,
    FpsCounter,
    AssetLoaderStats,
)
from engine.entities.components.effects import (
    FillTransition,
    SizeLayoutTransition,
)
from engine.entities.layout import (
    Flex,
    FlexDirection,
    Scene,
    ScreenSizeLayout,
    Padding,
    EdgeInset,
    Expanded,
    Viewport3d,
)
from engine.models import Size, Position, FrameContext, Constraints, Color
from engine.threed.entities.basic import Entity3d
from engine.threed.entities.components.base import Component3d
from engine.threed.entities.components.effects import (
    Position3dTransition,
    Rotation3dTransition,
)
from engine.threed.models import Camera, Position3d, Size3d, Quaternion
from engine.threed.entities.basic import Dice
from engine.renderer import Renderer


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

    def destroy(self):
        for component in self.components:
            component.destroy(self)

        self.entities[self.state.current].destroy()

    def paint(self, ctx: FrameContext, position: Position):
        for component in self.components:
            component.before_paint(self, ctx, position, self._size, self._state)

        if self._state.current != self.last_curr:
            curr = self.entities[self.state.current]
            last = self.entities[self.last_curr]
            curr.create(self.canvas)
            self.canvas.tag_raise(curr.id, last.id)
            last.destroy()
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


class GrabCursor(Component3d):
    def create(self, entity):
        self.entity = entity
        for id in entity.ids:
            entity.canvas.tag_bind(id, "<Enter>", self.enter)
            entity.canvas.tag_bind(id, "<Leave>", self.leave)

    def enter(self, e):
        self.entity.canvas.config(cursor="hand2")

    def leave(self, e):
        self.entity.canvas.config(cursor="")


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
        self.drag_start = self.camera.screen_to_world(e.x, e.y, self.entity.state.position.z)

    def drag(self, e):
        if self.camera is None:
            return

        world_pos = self.camera.screen_to_world(
            e.x, e.y, self.entity.state.position.z
        )

        if self.dragging:
            self.entity.state.position.x += world_pos.x - self.drag_start.x
            self.entity.state.position.y += world_pos.y - self.drag_start.y
            self.drag_start = Position3d(x=world_pos.x, y=world_pos.y, z=0)

    def release(self, e):
        self.dragging = False

class Throwable(Component3d):
    def __init__(self):
        self.dragging = False
        self.drag_start = Position3d(x=0, y=0, z=0)
        self.camera = None
        self.speed = Position3d(x=0, y=0, z=0)
        self.last_move = timer()

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

        l_screen_pos = camera.project(entity.state.position.sub(Position3d(entity.state.size.width / 2, 0 ,0)))
        r_screen_pos = camera.project(entity.state.position.add(Position3d(entity.state.size.width / 2, 0 ,0)))
        t_screen_pos = camera.project(entity.state.position.sub(Position3d(0, entity.state.size.height / 2 ,0)))
        b_screen_pos = camera.project(entity.state.position.add(Position3d(0, entity.state.size.height / 2 ,0)))

        top_left = camera.screen_to_world(0, 0, entity.state.position.z)
        bottom_right = camera.screen_to_world(camera.size[0], camera.size[1], entity.state.position.z)

        if l_screen_pos[0] < 0:
            self.speed.x *= -1
            entity.state.position.x = top_left.x + entity.state.size.width / 2
        if r_screen_pos[0] > camera.size[0]:
            self.speed.x *= -1
            entity.state.position.x = bottom_right.x - entity.state.size.width / 2
        if t_screen_pos[1] < 0:
            self.speed.y *= -1
            entity.state.position.y = top_left.y + entity.state.size.height / 2
        if b_screen_pos[1] > camera.size[1]:
            self.speed.y *= -1
            entity.state.position.y = bottom_right.y - entity.state.size.height / 2

        if not self.dragging:
            entity.state.position = entity.state.position.add(self.speed.mul(ctx.delta_time)) 
            decelleration = 0.99
            self.speed.x *= decelleration
            self.speed.y *= decelleration
            self.speed.z *= decelleration

    def click(self, e):
        if self.camera is None:
            return

        self.dragging = True
        self.drag_start = self.camera.screen_to_world(e.x, e.y, self.entity.state.position.z)
        self.last_move = timer()

    def drag(self, e):
        if self.camera is None:
            return

        world_pos = self.camera.screen_to_world(
            e.x, e.y, self.entity.state.position.z
        )


        if self.dragging:
            now = timer()
            delta = now - self.last_move

            self.speed = Position3d(
                x=(world_pos.x - self.drag_start.x) / delta,
                y=(world_pos.y - self.drag_start.y) / delta,
                z=0,
            )
            self.entity.state.position.x += world_pos.x - self.drag_start.x
            self.entity.state.position.y += world_pos.y - self.drag_start.y
            self.drag_start = Position3d(x=world_pos.x, y=world_pos.y, z=0)
            self.last_move = now

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


scene = RootScene(
    children=[
        ScreenSizeLayout(
            child=Viewport3d(
                camera=Camera(
                    position=Position3d(x=0, y=0, z=-300),
                    fov=50,
                ),
                children=[
                    Dice(
                        position=Position3d(x=0, y=0, z=0),
                        size=Size3d(width=10, height=10, depth=10),
                        components=[
                            GrabCursor(),
                            ChangeRotation(),
                            Rotation3dTransition(),
                            Throwable(),
                        ],
                    )
                ],
            )
        ),
        ScreenSizeLayout(
            child=Padding(
                components=[PaddingEffect(start=0, end=20, duration=1, repeat_times=3)],
                padding=EdgeInset.all(20),
                child=Scene(
                    children=[
                        Rect(
                            fill=Color.white(),
                            size=Size(width=140, height=50),
                            child=Padding(
                                padding=EdgeInset.symmetric(10, 5),
                                child=Flex(
                                    direction=FlexDirection.Column,
                                    children=[
                                        Expanded(),
                                        Text(
                                            components=[FpsCounter()],
                                            text="",
                                        ),
                                        Text(
                                            components=[
                                                AssetLoaderStats(),
                                            ],
                                            text="",
                                        ),
                                        Expanded(),
                                    ],
                                ),
                            ),
                        ),
                    ]
                ),
            )
        ),
    ]
)

asset_folder = os.path.join(os.path.dirname(__file__), "assets")
game = Renderer(800, 600, scene, asset_folder, bg=Color.from_hex("#1A1423"))
# game.asset_manager.register('hero', Asset(AssetType.Still, 'assets/hero.png'), [(i, 100) for i in range(100, 201)])
game.asset_manager.register("hero2", Asset(AssetType.Still, "hero.jpg"))
game.asset_manager.register(
    "small", Asset(AssetType.Still, "small.png", Resampling.NEAREST)
)
game.asset_manager.start()
