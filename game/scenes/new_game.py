from tkinter.font import Font
from typing import Callable
from engine.entities.basic import AnimatedSprite, Entity, Rect, Text
from engine.entities.components.base import Hook
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
from game.state import PlayerState, State
from game.theme_colors import ThemeColors
from game.widgets.button import Button


class ChoosePlayerButton:
    @staticmethod
    def build(n: int):
        return Expanded(
            child=Button.build(
                title=f"{n} Players",
                on_click=lambda *_: State.game.create_players(n),
                size="lg",
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
                        ChoosePlayerButton.build(2),
                        ChoosePlayerButton.build(3),
                    ],
                ),
                Flex(
                    direction=FlexDirection.Row,
                    children=[
                        ChoosePlayerButton.build(4),
                        ChoosePlayerButton.build(5),
                    ],
                ),
            ],
        )


class ChooseNPlayers:
    @staticmethod
    def build():
        return SizeBox(
            width=450,
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
    def build(player: PlayerState):
        return Rect(
            fill=ThemeColors.muted(),
            outline_width=0,
            child=Padding(
                padding=EdgeInset.all(10),
                child=Flex(
                    direction=FlexDirection.Row,
                    align=Alignment.Center,
                    gap=8,
                    children=[
                        Text(
                            text=player.name,
                            fill=ThemeColors.fg_inverse(),
                            font=Font(size=14),
                        ),
                        Expanded(),
                        Text(
                            text="show",
                            components=[
                                SetCursor(cursor="hand1"),
                                OnClick(
                                    callback=lambda *_: State.toggle_shown_player(
                                        player
                                    )
                                ),
                                Hook(
                                    before_layout=lambda entity, *_: setattr(
                                        entity.state,
                                        "text",
                                        "hide"
                                        if player == State.shown_player
                                        else "show",
                                    )
                                ),
                            ],
                            font=Font(weight="bold", size=14, underline=True),
                            fill=ThemeColors.fg_inverse(),
                        ),
                        Text(
                            text="(0)",
                            fill=ThemeColors.fg_inverse(),
                            components=[
                                Hook(
                                    before_layout=lambda entity, *_: setattr(
                                        entity.state,
                                        "text",
                                        f"({player.revealed_times})",
                                    )
                                )
                            ],
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
            width=450,
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
                                        children=[
                                            PlayerItem.build(p)
                                            for p in State.game.humans()
                                        ],
                                    ),
                                ),
                                Expanded(
                                    child=Center(
                                        child=EntitySwitch(
                                            current=False,
                                            components=[
                                                Hook(
                                                    before_layout=lambda entity, *_: setattr(
                                                        entity.state,
                                                        "current",
                                                        State.shown_player is not None,
                                                    )
                                                )
                                            ],
                                            entities={
                                                True: lambda: Rect(
                                                    outline_width=4,
                                                    fill=ThemeColors.bg_secondary(),
                                                    child=AnimatedSprite(
                                                        components=[
                                                            Hook(
                                                                before_layout=lambda entity, *_: entity.set_asset_key(
                                                                    State.shown_player.character.idle_asset_key  # type: ignore
                                                                )
                                                            )
                                                        ],
                                                        asset_key=State.shown_player.character.idle_asset_key,  # type: ignore
                                                        size=Size.square(200),
                                                    ),
                                                ),
                                                False: lambda: Text(
                                                    text="Avatar Preview",
                                                    font=Font(size=18, weight="bold"),
                                                    fill=ThemeColors.fg_muted(),
                                                ),
                                            },
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
                                on_click=lambda *_: State.set_scene("game"),
                            ),
                        ],
                    ),
                ],
            ),
        )


class NewGame:
    section_titles: dict[State.NewGameSection, str] = {
        "choose_n_players": "Pick the number of players",
        "view_characters": "Let every player privately view their character.\nMake sure that no other player can see.\nYou can see the number of times a character has been revealed in parentheses.",
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
                                    SizeBox(
                                        width=450,
                                        child=Text(
                                            components=[
                                                Hook(
                                                    before_layout=lambda entity, *_: setattr(
                                                        entity.state,
                                                        "text",
                                                        NewGame.section_titles[
                                                            State.new_game_section
                                                        ],
                                                    )
                                                ),
                                            ],
                                            text=NewGame.section_titles[
                                                State.new_game_section
                                            ],
                                            fill=ThemeColors.fg(),
                                            font=Font(size=14),
                                        ),
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
