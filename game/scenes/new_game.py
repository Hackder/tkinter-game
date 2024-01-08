from tkinter.font import Font
from typing import Callable
from engine.entities.basic import AnimatedSprite, Entity, Rect, Text
from engine.entities.components.base import Hook
from engine.entities.components.debug import DebugBounds
from engine.entities.components.effects import SetCursor
from engine.entities.components.events import OnClick
from engine.entities.conditional import EntitySwitch, Reactive
from engine.entities.layout import (
    Alignment,
    Center,
    Expanded,
    Flex,
    FlexDirection,
    Padding,
    Scene,
    SizeBox,
    Stack,
)
from engine.models import EdgeInset, Position, Size
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
                            text=lambda: player.name,
                            fill=ThemeColors.fg_inverse(),
                            font=Font(size=14),
                        ),
                        Expanded(),
                        Text(
                            text=lambda: "hide"
                            if player == State.shown_player
                            else "show",
                            components=[
                                SetCursor(cursor="hand1"),
                                OnClick(
                                    callback=lambda *_: State.toggle_shown_player(
                                        player
                                    )
                                ),
                            ],
                            font=Font(weight="bold", size=14, underline=True),
                            fill=ThemeColors.fg_inverse(),
                        ),
                        Text(
                            text=lambda: f"({player.revealed_times})",
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
                                            current=lambda: State.shown_player
                                            is not None,
                                            entities={
                                                True: lambda: Rect(
                                                    outline_width=4,
                                                    fill=ThemeColors.bg_secondary(),
                                                    child=AnimatedSprite(
                                                        asset_key=lambda: State.shown_player.character.idle_asset_key
                                                        if State.shown_player
                                                        else "",
                                                        size=Size.square(200),
                                                    ),
                                                ),
                                                False: lambda: Text(
                                                    text=lambda: "Avatar Preview",
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
                                title="Next",
                                on_click=lambda *_: State.set_new_game_section(
                                    "view_board"
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )


class BoardPreview:
    @staticmethod
    def build():
        return SizeBox(
            width=200,
            height=200,
            child=Reactive(
                dependency=lambda: State.game.board,
                builder=lambda: Scene(
                    children=[
                        Rect(
                            fill=ThemeColors.fg(),
                            position=Position(x=room.x * 5, y=room.y * 5 + 100),
                            size=Size(width=room.width * 5, height=room.height * 5),
                        )
                        for room in State.game.board
                    ],
                ),
            ),
        )


class ViewBoard:
    @staticmethod
    def build():
        State.game.generate_board()

        return SizeBox(
            width=450,
            height=300,
            child=Flex(
                direction=FlexDirection.Column,
                align=Alignment.Center,
                gap=16,
                children=[
                    Expanded(
                        child=Center(
                            child=BoardPreview.build(),
                        ),
                    ),
                    Flex(
                        direction=FlexDirection.Row,
                        children=[
                            Button.build(
                                title="Regenerate",
                                on_click=lambda *_: State.game.generate_board(),
                            ),
                            Expanded(),
                            Button.build(
                                title="Back",
                                on_click=lambda *_: State.set_new_game_section(
                                    "view_characters"
                                ),
                            ),
                            Button.build(
                                title="Start game",
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
        "view_board": "View the generated game board.",
    }

    section_map: dict[State.NewGameSection, Callable[[], Entity]] = {
        "choose_n_players": ChooseNPlayers.build,
        "view_characters": ViewPlayers.build,
        "view_board": ViewBoard.build,
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
                                        text=lambda: "New Game",
                                        fill=ThemeColors.fg(),
                                        font=Font(size=18, weight="bold"),
                                    ),
                                    SizeBox(
                                        width=450,
                                        child=Text(
                                            text=lambda: NewGame.section_titles[
                                                State.new_game_section
                                            ],
                                            fill=ThemeColors.fg(),
                                            font=Font(size=14),
                                        ),
                                    ),
                                ],
                            ),
                            EntitySwitch(
                                current=lambda: State.new_game_section,
                                entities=NewGame.section_map,
                            ),
                        ],
                    ),
                ),
            ),
        )
