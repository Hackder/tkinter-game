from tkinter.font import Font
from engine.entities.basic import Rect, Text
from engine.entities.components.debug import DebugBounds
from engine.entities.conditional import EntitySwitch
from engine.entities.layout import (
    Center,
    Expanded,
    Flex,
    FlexDirection,
    Padding,
    SizeBox,
)
from engine.models import EdgeInset
from game.state import State
from game.theme_colors import ThemeColors
from game.widgets.button import Button


class ChoosePlayerGrid:
    @staticmethod
    def build():
        return (
            Flex(
                direction=FlexDirection.Column,
                children=[
                    Flex(
                        direction=FlexDirection.Row,
                        children=[
                            Expanded(
                                child=Button.build(
                                    title="2 Players",
                                    size="md",
                                    on_click=lambda *_: NewGameState.set_players(2),
                                ),
                            ),
                            Expanded(
                                child=Button.build(
                                    title="3 Players",
                                    size="md",
                                    on_click=lambda *_: NewGameState.set_players(3),
                                ),
                            ),
                        ],
                    ),
                    Flex(
                        direction=FlexDirection.Row,
                        children=[
                            Expanded(
                                child=Button.build(
                                    title="4 Players",
                                    size="md",
                                    on_click=lambda *_: NewGameState.set_players(4),
                                ),
                            ),
                            Expanded(
                                child=Button.build(
                                    title="5 Players",
                                    size="md",
                                    on_click=lambda *_: NewGameState.set_players(5),
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )


class ChooseNPlayers:
    @staticmethod
    def build():
        return Center(
            child=Rect(
                fill=ThemeColors.background_secondary(),
                outline_width=0,
                child=Padding(
                    padding=EdgeInset.all(20),
                    child=SizeBox(
                        width=300,
                        child=Flex(
                            direction=FlexDirection.Column,
                            gap=16,
                            children=[
                                Text(
                                    text="New Game",
                                    fill=ThemeColors.foreground(),
                                    font=Font(size=18, weight="bold"),
                                ),
                                *ChoosePlayerGrid.build(),
                                Flex(
                                    direction=FlexDirection.Row,
                                    gap=8,
                                    children=[
                                        Expanded(),
                                        Button.build(
                                            title="Back",
                                            size="md",
                                            on_click=lambda *args: setattr(
                                                State, "scene", "menu"
                                            ),
                                        ),
                                        Button.build(title="Next", size="md"),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ),
            )
        )


class NewGameState:
    section: str = "choose_n_players"
    number_of_players: int | None = None

    @staticmethod
    def set_players(n: int):
        NewGameState.number_of_players = n


class NewGame:
    @staticmethod
    def build():
        return EntitySwitch(
            current="choose_n_players",
            entities={
                "choose_n_players": ChooseNPlayers.build,
            },
        )
