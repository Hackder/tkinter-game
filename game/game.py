from typing import Callable
from engine.entities.basic import Entity, RootScene
from engine.entities.conditional import EntitySwitch
from engine.entities.layout import (
    ScreenSizeLayout,
    Stack,
)
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
    ]
)
