from engine.entities.basic import AnimatedSprite, RootScene, Sprite
from engine.entities.components.base import Hook
from engine.entities.conditional import EntitySwitch
from engine.entities.layout import (
    ScreenSizeLayout,
    Stack,
)
from engine.models import Size

from game.scenes.main_menu import MainMenu
from game.scenes.metrics import Metrics
from game.scenes.free_cube import FreeCube
from game.scenes.new_game import NewGame
from game.state import State


scene = RootScene(
    children=[
        ScreenSizeLayout(
            child=EntitySwitch(
                current="menu",
                components=[
                    Hook(
                        before_layout=lambda entity, *_: setattr(
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
