from engine.entities.basic import Entity, Rect, Text
from engine.entities.components.debug import DebugBounds
from engine.entities.components.events import OnClick, OnDrag
from engine.entities.components.layout import Translate
from engine.entities.layout import Center, Scene, SizeBox, Stack
from engine.models import Color, Position, Size
from game.state import RoomState, State
from game.theme_colors import ThemeColors


class GameRoom:
    @staticmethod
    def build(room: RoomState, scale: float = 32) -> Entity:
        return Stack(
            components=[
                Translate(position=Position(x=room.x * scale, y=room.y * scale))
            ],
            children=[
                Rect(
                    tag="draggable",
                    fill=ThemeColors.bg_secondary(),
                    size=Size(width=room.width * scale, height=room.height * scale),
                ),
                Scene(
                    children=[
                        *[
                            Rect(
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
                            *[GameRoomHalo.build(room) for room in State.game.board],
                            *[GameRoom.build(room) for room in State.game.board],
                        ],
                    ),
                ),
            ],
        )
