import copy
from tkinter import Canvas
from typing import Any

from engine.entities.basic import Entity, Rect, RootScene
from engine.entities.components.base import Component
from engine.entities.components.events import OnClick
from engine.entities.layout import (
    Expanded,
    Flex,
    FlexDirection,
    Padding,
    ScreenSizeLayout,
    Stack,
)
from engine.models import Color, Constraints, EdgeInset, FrameContext, Position, Size

from game.scenes.main_menu import MainMenu
from game.scenes.metrics import Metrics
from game.scenes.free_cube import FreeCube


class EntitySwitchState:
    def __init__(self, current: str):
        self.current = current
        self._last = current

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
        current: str,
        entities: dict[str, Entity],
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.state = EntitySwitchState(current=current)
        self._state = self.state.copy()
        self.entities = entities
        self._size = Size(width=0, height=0)

    def current(self) -> Entity:
        if self.state.current not in self.entities:
            raise ValueError(
                f"EntitySwitch: no entity with name '{self.state.current}'"
            )

        return self.entities[self.state.current]

    def create(self, canvas: Canvas):
        self.canvas = canvas
        for component in self.components:
            component.create(self)

        self.current().create(canvas)

    def destroy(self, entity: Entity):
        for component in self.components:
            component.destroy(self)

        self.current().destroy(self)

    def paint(self, ctx: FrameContext, position: Position):
        for component in self.components:
            component.before_paint(self, ctx, position, self._size, self._state)

        self.entities[self._state.current].paint(ctx, position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        if self.state.current != self.state._last:
            curr = self.entities[self.state.current]
            curr.create(self.canvas)
            last = self.entities[self.state._last]
            last.destroy(self)
            self.state._last = self.state.current
            state._last = self.state._last
            state.current = self.state.current

        self._state = state

        child_size = self.current().layout(ctx, constraints)
        self.current()._size = child_size

        return child_size


class Hook(Component):
    def __init__(self, *, before_paint=None, before_layout=None):
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


class State:
    def __init__(self):
        self.scene = "menu"


global_state = State()

scene = RootScene(
    children=[
        EntitySwitch(
            current="menu",
            components=[
                Hook(
                    before_layout=lambda entity, *rest: setattr(
                        entity.state, "current", global_state.scene
                    )
                ),
            ],
            entities={
                "menu": ScreenSizeLayout(
                    child=Stack(
                        children=[
                            FreeCube.build(),
                            MainMenu.build(),
                            Metrics.build(),
                        ]
                    )
                ),
                "other": ScreenSizeLayout(
                    child=Metrics.build(),
                ),
            },
        ),
        ScreenSizeLayout(
            child=Padding(
                padding=EdgeInset.all(20),
                child=Flex(
                    direction=FlexDirection.Column,
                    children=[
                        Expanded(),
                        Rect(
                            size=Size(width=100, height=100),
                            fill=Color.red(),
                            components=[
                                OnClick(
                                    lambda *args: setattr(
                                        global_state, "scene", "other"
                                    )
                                ),
                            ],
                        ),
                        Rect(
                            size=Size(width=100, height=100),
                            fill=Color.green(),
                            components=[
                                OnClick(
                                    lambda *args: setattr(global_state, "scene", "menu")
                                ),
                            ],
                        ),
                    ],
                ),
            )
        ),
    ]
)
