from tkinter.font import Font
from typing import Any, Callable
from engine.entities.basic import AnimatedSprite, Entity, Rect, Text
from engine.entities.components.base import Hook
from engine.entities.components.debug import DebugBounds
from engine.entities.components.effects import SetCursor
from engine.entities.components.events import OnClick
from engine.entities.conditional import EntitySwitch
from engine.entities.layout import (
    Alignment,
    Center,
    Expanded,
    Flex,
    FlexDirection,
    Padding,
    SizeBox,
)
from engine.models import EdgeInset, Size
from game.state import State
from game.theme_colors import ThemeColors
from game.widgets.button import Button


class ChoosePlayerButton:
    @staticmethod
    def build(n: int):
        return Expanded(
            child=Button.build(
                title=f"{n} Players",
                on_click=lambda *_: State.game.create_players(n),
            ),
        )


class ChoosePlayerGrid:
    @staticmethod
    def build():
        return Flex(
            direction=FlexDirection.Column,
            children=[
                Flex(
                    direction=FlexDirection.Row,
                    children=[
                        ChoosePlayerButton.build(1),
                        ChoosePlayerButton.build(2),
                    ],
                ),
                Flex(
                    direction=FlexDirection.Row,
                    children=[
                        ChoosePlayerButton.build(3),
                        ChoosePlayerButton.build(4),
                    ],
                ),
            ],
        )


class ChooseNPlayers:
    @staticmethod
    def build():
        return SizeBox(
            width=300,
            child=Flex(
                direction=FlexDirection.Column,
                gap=16,
                children=[
                    ChoosePlayerGrid.build(),
                    Flex(
                        direction=FlexDirection.Row,
                        gap=8,
                        children=[
                            Expanded(),
                            Button.build(
                                title="Back",
                                on_click=lambda *_: setattr(State, "scene", "menu"),
                            ),
                        ],
                    ),
                ],
            ),
        )


class PlayerItem:
    @staticmethod
    def build():
        return Rect(
            fill=ThemeColors.muted(),
            outline_width=0,
            child=Padding(
                padding=EdgeInset.all(10),
                child=Flex(
                    direction=FlexDirection.Row,
                    align=Alignment.Center,
                    children=[
                        Text(
                            text="Player 1",
                            fill=ThemeColors.fg_inverse(),
                            font=Font(size=14),
                        ),
                        Expanded(),
                        Text(
                            text="show",
                            components=[SetCursor(cursor="hand1")],
                            font=Font(weight="bold", size=14, underline=True),
                            fill=ThemeColors.fg_inverse(),
                        ),
                    ],
                ),
            ),
        )


class ViewPlayers:
    @staticmethod
    def build():
        global character
        return SizeBox(
            width=500,
            height=300,
            child=Flex(
                direction=FlexDirection.Column,
                gap=16,
                children=[
                    Expanded(
                        child=Flex(
                            tag="test",
                            direction=FlexDirection.Row,
                            align=Alignment.Stretch,
                            gap=8,
                            children=[
                                SizeBox(
                                    width=160,
                                    child=Flex(
                                        direction=FlexDirection.Column,
                                        gap=8,
                                        children=[PlayerItem.build() for _ in range(5)],
                                    ),
                                ),
                                Expanded(
                                    child=Center(
                                        # child=Text(
                                        #     text="Avatar Preview",
                                        #     font=Font(size=18, weight="bold"),
                                        #     fill=ThemeColors.fg_muted(),
                                        # ),
                                        child=Rect(
                                            outline_width=4,
                                            fill=ThemeColors.bg_secondary(),
                                            child=AnimatedSprite(
                                                asset_key="character1-idle",
                                                size=Size.square(200),
                                            ),
                                        ),
                                    ),
                                ),
                            ],
                        )
                    ),
                    Flex(
                        direction=FlexDirection.Row,
                        children=[
                            Expanded(),
                            Button.build(
                                title="Back",
                                on_click=lambda *_: State.set_new_game_section(
                                    "choose_n_players"
                                ),
                            ),
                            Button.build(
                                title="Start",
                                on_click=lambda *_: setattr(State, "scene", "game"),
                            ),
                        ],
                    ),
                ],
            ),
        )


class NewGame:
    section_titles: dict[State.NewGameSection, str] = {
        "choose_n_players": "Pick the number of players",
        "view_characters": "View characters",
    }

    section_map: dict[State.NewGameSection, Callable[[], Entity]] = {
        "choose_n_players": ChooseNPlayers.build,
        "view_characters": ViewPlayers.build,
    }

    @staticmethod
    def build():
        return Center(
            child=Rect(
                fill=ThemeColors.bg_secondary(),
                outline_width=0,
                child=Padding(
                    padding=EdgeInset.all(20),
                    child=Flex(
                        direction=FlexDirection.Column,
                        gap=16,
                        children=[
                            Flex(
                                direction=FlexDirection.Column,
                                children=[
                                    Text(
                                        text="New Game",
                                        fill=ThemeColors.fg(),
                                        font=Font(size=18, weight="bold"),
                                    ),
                                    Text(
                                        components=[
                                            Hook(
                                                before_layout=lambda entity, *_: setattr(
                                                    entity.state,
                                                    "text",
                                                    NewGame.section_titles[
                                                        State.new_game_section
                                                    ],
                                                )
                                            )
                                        ],
                                        text=NewGame.section_titles[
                                            State.new_game_section
                                        ],
                                        fill=ThemeColors.fg(),
                                        font=Font(size=14),
                                    ),
                                ],
                            ),
                            EntitySwitch(
                                components=[
                                    Hook(
                                        before_layout=lambda entity, *_: setattr(
                                            entity.state,
                                            "current",
                                            State.new_game_section,
                                        )
                                    ),
                                ],
                                current="choose_n_players",
                                entities=NewGame.section_map,
                            ),
                        ],
                    ),
                ),
            ),
        )
