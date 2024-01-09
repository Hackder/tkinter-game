import random
from tkinter.font import Font
from typing import Any
from engine.animation.utils import Easing
from engine.entities.basic import AnimatedSprite, Entity, Rect, Text
from engine.entities.components.base import (
    Bind,
    Component,
    Hook,
    LeaveOriginal,
    PaintBind,
    PositionGroup,
)
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
    StartOnFill,
    StartOnTop,
)
from engine.entities.components.layout import Translate
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
from engine.entities.state import EntityState
from engine.models import Color, EdgeInset, FrameContext, Position, Size
from engine.state import SimpleState
from game.state import PlayerState, RoomState, State
from game.theme_colors import ThemeColors
from game.widgets.button import Button


class GameRoom:
    @staticmethod
    def build(room: RoomState) -> Entity:
        fill = ThemeColors.bg_secondary()
        if room == State.game.start_room:
            fill = ThemeColors.bg_tertiary()
        elif room == State.game.end_room:
            fill = ThemeColors.gold()

        return Stack(
            components=[
                Translate(
                    position=Position(
                        x=room.x * State.game.scale, y=room.y * State.game.scale
                    )
                )
            ],
            children=[
                Rect(
                    tag="draggable",
                    fill=fill,
                    size=Size(
                        width=room.width * State.game.scale,
                        height=room.height * State.game.scale,
                    ),
                ),
                Scene(
                    children=[
                        *[
                            Rect(
                                tag="draggable",
                                components=[
                                    Translate(
                                        position=Position(
                                            y=0, x=(i + 1) * State.game.scale
                                        )
                                    )
                                ],
                                size=Size(
                                    width=1, height=room.height * State.game.scale
                                ),
                                outline_width=0,
                                fill=ThemeColors.bg(),
                            )
                            for i in range(room.width)
                        ],
                        *[
                            Rect(
                                tag="draggable",
                                components=[
                                    Translate(
                                        position=Position(
                                            x=0, y=(i + 1) * State.game.scale
                                        )
                                    )
                                ],
                                size=Size(
                                    width=room.width * State.game.scale, height=1
                                ),
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
    def build(room: RoomState, size: float = 10) -> Entity:
        return SizeBox(
            width=room.width * State.game.scale + size * 2,
            height=room.height * State.game.scale + size * 2,
            components=[
                Translate(
                    position=Position(
                        x=room.x * State.game.scale - size,
                        y=room.y * State.game.scale - size,
                    )
                ),
            ],
            child=Stack(
                children=[
                    Rect(
                        tag="draggable",
                        fill=ThemeColors.muted(),
                        outline_width=0,
                        size=Size(
                            width=room.width * State.game.scale + size * 2,
                            height=room.height * State.game.scale + size * 2,
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
                        PositionGroup(
                            components=[
                                Translate(get_position=lambda: get_offset()),
                                PositionTransition(
                                    easing=Easing.ease_out, duration=0.2
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        )


class RandomWander(Component):
    def __init__(self, enabled: bool = True, scale: float = 32):
        self.enabled = enabled
        self.scale = scale
        self.random_offset = self.get_random_position()

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        if random.random() < 0.1 * ctx.delta_time and self.enabled:
            self.random_offset = self.get_random_position()

        position.mut_add(self.random_offset)

    def get_random_position(self):
        rand_x = (random.random() * 2 - 1) * self.scale * 0.4
        rand_y = (random.random() * 2 - 1) * self.scale * 0.4
        return Position(x=rand_x, y=rand_y)


class WalkOnPosChange(Component):
    def __init__(self, walk_asset_key: str):
        self.walk_asset_key = walk_asset_key
        self.last_pos = Position.zero()

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        if self.last_pos != position:
            if state is None:
                raise Exception("State is required")
            state.asset_key = self.walk_asset_key
            self.last_pos = position.copy()


class YDepthSort(Component):
    def __init__(self, store: list[tuple[Entity, float]]):
        self.store = store

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        inserted_at = 0
        for i, (e, y) in enumerate(self.store):
            if y > position.y:
                self.store.insert(i, (entity, position.y))
                inserted_at = i
                break
        else:
            self.store.append((entity, position.y))
            inserted_at = len(self.store) - 1

        for i in range(inserted_at + 1, len(self.store)):
            e, y = self.store[i]
            e.canvas.tag_raise(e.id)


class GamePlayer:
    @staticmethod
    def build(p: PlayerState, y_sort_store: list[tuple[Entity, float]]) -> Entity:
        player_scale = 1.2

        return Stack(
            components=[
                Translate(
                    get_position=lambda: Position(
                        x=p.x * State.game.scale + State.game.scale * 0.1,
                        y=p.y * State.game.scale
                        - State.game.scale * (player_scale - 0.5),
                    )
                ),
            ],
            children=[
                AnimatedSprite(
                    asset_key=lambda: p.character.idle_asset_key,
                    size=Size(
                        width=State.game.scale * player_scale,
                        height=State.game.scale * player_scale,
                    ),
                    components=[
                        PositionGroup(
                            components=[
                                RandomWander(scale=State.game.scale),
                                PositionTransition(speed=20),
                                WalkOnPosChange(
                                    walk_asset_key=p.character.walk_asset_key
                                ),
                            ]
                        ),
                        YDepthSort(y_sort_store),
                        OnMouseEnter(callback=lambda *_: State.set_hovered_player(p)),
                        OnMouseLeave(
                            callback=lambda *_: State.set_hovered_player(None)
                        ),
                        OnClick(callback=lambda *_: State.set_selected_player(p)),
                        SetCursor(cursor="hand1"),
                    ],
                )
            ],
        )


class AvailableTiles:
    @staticmethod
    def create_tile(x: int, y: int, distance) -> Entity:
        hoverred = SimpleState(False)
        return Rect(
            fill=Color.from_hex("#565264"),
            size=Size.square(State.game.scale),
            components=[
                Translate(
                    position=Position(
                        x=x * State.game.scale,
                        y=y * State.game.scale,
                    )
                ),
                StartOnFill(
                    fill=ThemeColors.bg_secondary(),
                    delay=distance * 0.07,
                ),
                FillTransition(
                    duration=0.3,
                    easing=Easing.ease_in_out,
                ),
                OnMouseEnter(callback=lambda *_: hoverred.set(True)),
                OnMouseLeave(callback=lambda *_: hoverred.set(False)),
                PaintBind(
                    "fill",
                    lambda: ThemeColors.gold() if hoverred.get() else LeaveOriginal(),
                ),
                SetCursor(cursor="hand2"),
                OnClick(callback=lambda *_: State.move_selected_player_to(x, y)),
            ],
        )

    @staticmethod
    def create_tiles() -> list[Entity]:
        p = State.selected_player
        if p is None:
            return []

        tiles: list[Entity] = []

        for distance in range(State.game.available_stemps + 1):
            for x in range(-distance, distance + 1):
                for y in range(-distance, distance + 1):
                    if abs(x) + abs(y) != distance:
                        continue

                    for room in State.game.board:
                        if (
                            room.x <= p.x + x < room.x + room.width
                            and room.y <= p.y + y < room.y + room.height
                        ):
                            break
                    else:
                        continue

                    tiles.append(AvailableTiles.create_tile(p.x + x, p.y + y, distance))

        return tiles

    @staticmethod
    def build() -> Entity:
        return Reactive(
            dependency=lambda: State.selected_player,
            builder=lambda: EntitySwitch(
                current=lambda: State.selected_player is not None,
                entities={
                    True: lambda: Scene(
                        children=AvailableTiles.create_tiles(),
                    ),
                    False: lambda: Scene(),
                },
            ),
        )


class Game:
    @staticmethod
    def build() -> Entity:
        y_sort_store = []

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
                                GameRoomHalo.build(room, 10)
                                for room in State.game.board
                            ],
                            *[GameRoom.build(room) for room in State.game.board],
                            AvailableTiles.build(),
                            *[
                                GamePlayer.build(p, y_sort_store)
                                for p in State.game.players
                            ],
                            Scene(
                                components=[
                                    Hook(before_paint=lambda *_: y_sort_store.clear())
                                ]
                            ),
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
