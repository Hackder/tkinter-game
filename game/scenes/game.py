import random
from tkinter.font import Font
from engine.animation.utils import Easing
from engine.entities.basic import AnimatedSprite, Entity, Rect, Text
from engine.entities.components.base import Bind
from engine.entities.components.debug import DebugBounds
from engine.entities.components.events import (
    OnClick,
    OnDrag,
    OnMouseEnter,
    OnMouseLeave,
)
from engine.entities.components.effects import (
    FillTransition,
    PositionTransition,
    SetCursor,
    StartOnTop,
)
from engine.entities.components.layout import Translate
from engine.entities.conditional import EntitySwitch
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
from game.state import PlayerState, RoomState, State
from game.theme_colors import ThemeColors
from game.widgets.button import Button


class GameRoom:
    @staticmethod
    def build(room: RoomState, scale: float = 32) -> Entity:
        fill = ThemeColors.bg_secondary()
        if room == State.game.start_room:
            fill = ThemeColors.bg_tertiary()
        elif room == State.game.end_room:
            fill = ThemeColors.gold()

        return Stack(
            components=[
                Translate(position=Position(x=room.x * scale, y=room.y * scale))
            ],
            children=[
                Rect(
                    tag="draggable",
                    fill=fill,
                    size=Size(width=room.width * scale, height=room.height * scale),
                ),
                Scene(
                    children=[
                        *[
                            Rect(
                                tag="draggable",
                                components=[
                                    Translate(position=Position(y=0, x=(i + 1) * scale))
                                ],
                                size=Size(width=1, height=room.height * scale),
                                outline_width=0,
                                fill=ThemeColors.bg(),
                            )
                            for i in range(room.width)
                        ],
                        *[
                            Rect(
                                tag="draggable",
                                components=[
                                    Translate(position=Position(x=0, y=(i + 1) * scale))
                                ],
                                size=Size(width=room.width * scale, height=1),
                                outline_width=0,
                                fill=ThemeColors.bg(),
                            )
                            for i in range(room.height)
                        ],
                    ]
                ),
            ],
        )


class GameRoomHalo:
    @staticmethod
    def build(room: RoomState, scale: float = 32, size: float = 10) -> Entity:
        return SizeBox(
            width=room.width * scale + size * 2,
            height=room.height * scale + size * 2,
            components=[
                Translate(
                    position=Position(x=room.x * scale - size, y=room.y * scale - size)
                ),
            ],
            child=Stack(
                children=[
                    Rect(
                        tag="draggable",
                        fill=ThemeColors.muted(),
                        outline_width=0,
                        size=Size(
                            width=room.width * scale + size * 2,
                            height=room.height * scale + size * 2,
                        ),
                    )
                ]
            ),
        )


class PauseMenu:
    @staticmethod
    def build() -> Entity:
        return Rect(
            fill=ThemeColors.bg(),
            components=[OnDrag(drag=print)],
            child=Center(
                child=Rect(
                    fill=ThemeColors.bg_secondary(),
                    size=Size(width=300, height=250),
                    components=[
                        StartOnTop(),
                        PositionTransition(easing=Easing.ease_out, duration=0.8),
                    ],
                    child=Padding(
                        padding=EdgeInset.all(20),
                        child=Flex(
                            direction=FlexDirection.Column,
                            align=Alignment.Stretch,
                            gap=10,
                            children=[
                                Flex(
                                    direction=FlexDirection.Row,
                                    children=[
                                        Expanded(),
                                        Text(
                                            text=lambda: "Game Paused",
                                            font=Font(size=24, weight="bold"),
                                            fill=ThemeColors.fg(),
                                        ),
                                        Expanded(),
                                    ],
                                ),
                                Expanded(),
                                Button.build(
                                    title="Resume",
                                    size="md",
                                    on_click=lambda *_: State.toggle_game_paused(),
                                ),
                                Button.build(
                                    title="Save Game",
                                    size="md",
                                    on_click=lambda *_: State.save_game("test"),
                                ),
                                Button.build(
                                    title="Main Menu",
                                    size="md",
                                    on_click=lambda *_: State.set_scene("menu"),
                                ),
                            ],
                        ),
                    ),
                )
            ),
        )


class GameUI:
    @staticmethod
    def build() -> Entity:
        return Padding(
            padding=EdgeInset.all(10),
            child=Flex(
                direction=FlexDirection.Column,
                align=Alignment.Stretch,
                children=[
                    Stack(
                        children=[
                            Flex(
                                direction=FlexDirection.Row,
                                children=[
                                    Expanded(),
                                    Rect(
                                        fill=ThemeColors.fg(),
                                        outline_width=2,
                                        components=[
                                            Translate(position=Position(x=0, y=-10))
                                        ],
                                        child=Padding(
                                            padding=EdgeInset(10, 20, 10, 20),
                                            child=Text(
                                                text=lambda: "Game",
                                                font=Font(size=24, weight="bold"),
                                                fill=ThemeColors.fg_inverse(),
                                            ),
                                        ),
                                    ),
                                    Expanded(),
                                ],
                            ),
                            Flex(
                                direction=FlexDirection.Row,
                                children=[
                                    Expanded(),
                                    Button.build(
                                        title="Pause",
                                        size="sm",
                                        on_click=lambda *_: State.toggle_game_paused(),
                                    ),
                                ],
                            ),
                        ]
                    ),
                    Expanded(),
                    GameUI.character_bar(),
                ],
            ),
        )

    @staticmethod
    def character_bar() -> Entity:
        return Flex(
            direction=FlexDirection.Row,
            gap=10,
            children=[
                Expanded(),
                *[CharacterBarIcon.build(p) for p in State.game.players],
                Expanded(),
            ],
        )


class CharacterBarIcon:
    @staticmethod
    def build(p: PlayerState) -> Entity:
        def hovered():
            return State.hovered_player == p

        def selected():
            return State.selected_player == p

        def get_offset():
            if hovered():
                return Position(x=0, y=-15)
            return Position(x=0, y=-5)

        tag = random.randbytes(8).hex()

        return Stack(
            children=[
                Rect(
                    tag=tag,
                    fill=ThemeColors.primary(),
                    size=Size(width=64, height=24),
                    components=[
                        Bind(
                            "fill",
                            lambda: ThemeColors.fg()
                            if hovered()
                            else ThemeColors.muted()
                            if selected()
                            else ThemeColors.primary(),
                        ),
                        SetCursor(cursor="hand1"),
                        Translate(position=Position(x=0, y=40)),
                        FillTransition(easing=Easing.ease_out, duration=0.2),
                    ],
                ),
                AnimatedSprite(
                    tag=tag,
                    asset_key=lambda: p.character.walk_asset_key
                    if selected()
                    else p.character.idle_asset_key,
                    size=Size(width=64, height=64),
                    paused=lambda: not hovered() and not selected(),
                    components=[
                        SetCursor(cursor="hand1"),
                        OnMouseEnter(
                            tag=tag, callback=lambda *_: State.set_hovered_player(p)
                        ),
                        OnMouseLeave(
                            tag=tag, callback=lambda *_: State.set_hovered_player(None)
                        ),
                        OnClick(
                            tag=tag,
                            callback=lambda *_: State.set_selected_player(
                                None if selected() else p
                            ),
                        ),
                        Translate(get_position=lambda: get_offset()),
                        PositionTransition(easing=Easing.ease_out, duration=0.2),
                    ],
                ),
            ],
        )


class Game:
    @staticmethod
    def build() -> Entity:
        return Stack(
            children=[
                Rect(
                    tag="draggable",
                    fill=ThemeColors.bg(),
                    outline_width=0,
                    components=[
                        OnDrag(
                            tag="draggable",
                            drag=lambda e, _: State.move_game_view(e.dx, e.dy),
                        ),
                    ],
                ),
                Center(
                    child=Scene(
                        components=[
                            Translate(get_position=lambda: State.game_view_offset),
                        ],
                        children=[
                            *[
                                GameRoomHalo.build(room, 50)
                                for room in State.game.board
                            ],
                            *[GameRoom.build(room, 50) for room in State.game.board],
                        ],
                    ),
                ),
                GameUI.build(),
                EntitySwitch(
                    current=lambda: State.game_paused,
                    entities={
                        True: PauseMenu.build,
                        False: Scene,
                    },
                ),
            ],
        )
