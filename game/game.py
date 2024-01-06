import copy
from tkinter import Canvas
from typing import Any, Callable

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
from game.state import State


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
        entities: dict[str, Callable[[], Entity]],
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
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        if self.state.current != self.state._last:
            self.current.destroy()
            self.current = self.entities[self.state.current]()
            self.current.create(self.canvas)

            self.state._last = self.state.current
            state._last = self.state._last
            state.current = self.state.current

        self._state = state

        child_size = self.current.layout(ctx, constraints)
        self.current._size = child_size

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


scene = RootScene(
    children=[
        EntitySwitch(
            current="menu",
            components=[
                Hook(
                    before_layout=lambda entity, *rest: setattr(
                        entity.state, "current", State.scene
                    )
                ),
            ],
            entities={
                "menu": lambda: ScreenSizeLayout(
                    child=Stack(
                        children=[
                            FreeCube.build(),
                            MainMenu.build(),
                            Metrics.build(),
                        ]
                    )
                ),
                "other": lambda: ScreenSizeLayout(
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
                                    callback=lambda *args: setattr(
                                        State, "scene", "other"
                                    )
                                ),
                            ],
                        ),
                        Rect(
                            size=Size(width=100, height=100),
                            fill=Color.green(),
                            components=[
                                OnClick(
                                    callback=lambda *args: setattr(
                                        State, "scene", "menu"
                                    )
                                ),
                            ],
                        ),
                    ],
                ),
            )
        ),
    ]
)
