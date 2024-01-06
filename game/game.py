from typing import Any

from engine.entities.basic import Entity, RootScene
from engine.entities.components.base import Component
from engine.entities.conditional import EntitySwitch
from engine.entities.layout import (
    ScreenSizeLayout,
    Stack,
)
from engine.models import FrameContext, Position, Size

from game.scenes.main_menu import MainMenu
from game.scenes.metrics import Metrics
from game.scenes.free_cube import FreeCube
from game.scenes.new_game import NewGame
from game.state import State


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
        ScreenSizeLayout(
            child=EntitySwitch(
                current="menu",
                components=[
                    Hook(
                        before_layout=lambda entity, *rest: setattr(
                            entity.state, "current", State.scene
                        )
                    ),
                ],
                entities={
                    "menu": lambda: Stack(
                        children=[
                            FreeCube.build(),
                            MainMenu.build(),
                        ]
                    ),
                    "metrics": Metrics.build,
                    "new_game": NewGame.build,
                },
            ),
        ),
        Metrics.build(),
    ]
)
