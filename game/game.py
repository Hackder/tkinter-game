from typing import Callable
from engine.entities.basic import Entity, Rect, RootScene
from engine.entities.components.debug import FpsFlicker
from engine.entities.conditional import EntitySwitch
from engine.entities.layout import (
    Scene,
    ScreenSizeLayout,
    Stack,
)
from engine.models import Position, Size
from engine.entities.components.layout import Translate
from game.scenes.game import Game

from game.scenes.main_menu import MainMenu
from game.scenes.free_cube import FreeCube
from game.scenes.metrics import Metrics
from game.scenes.new_game import NewGame
from game.state import State


scenes: dict[State.Scene, Callable[[], Entity]] = {
    "menu": lambda: Stack(
        children=[
            FreeCube.build(),
            MainMenu.build(),
        ]
    ),
    "new_game": NewGame.build,
    "game": Game.build,
}

scene = RootScene(
    children=[
        ScreenSizeLayout(
            child=EntitySwitch(
                current=lambda: State.scene,
                entities=scenes,
            ),
        ),
        Metrics.build(),
        ScreenSizeLayout(
            child=Scene(
                children=[
                    Rect(
                        size=Size.square(100),
                        components=[
                            Translate(position=Position(x=100, y=100)),
                            FpsFlicker(),
                        ],
                    )
                ],
            )
        ),
    ]
)
