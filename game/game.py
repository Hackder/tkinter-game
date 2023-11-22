from tkinter import Canvas
import copy

from PIL.Image import Resampling

from engine.animation.utils import Animation, AnimationDirection, AnimationEnd
from engine.assets import Asset, AssetType
from engine.entities.basic import Entity, Rect, RootScene, Sprite, Text
from engine.entities.components.base import Component
from engine.entities.components.debug import DebugBounds, FpsCounter, AssetLoaderStats, PrintLifecycle
from engine.entities.components.effects import FillTransition, PositionTransition, SquareShake, SizeLayoutTransition
from engine.entities.layout import Center, Flex, FlexDirection, Scene, ScreenSizeLayout, Padding, EdgeInset, Stack, Expanded
from engine.models import Size, Position, FrameContext, Constraints, Color
from engine.game import Game

class PaddingEffect(Component):
    def __init__(self, *, start: float, end: float, duration: float, repeat_times: int = 0):
        self.start = start
        self.end = end
        self.anim = Animation(duration=duration, direction=AnimationDirection.Alternate, repeat_times=repeat_times, end=AnimationEnd.End)

    def before_layout(self, entity, ctx, state):
        if state is None or not hasattr(state, 'padding'):
            raise Exception('PaddingEffect component must be on an entity which supports padding')

        value = self.anim.process(ctx.delta_time)

        state.padding.left += value * (self.end - self.start) + self.start
        state.padding.right += value * (self.end - self.start) + self.start
        state.padding.top += value * (self.end - self.start) + self.start
        state.padding.bottom += value * (self.end - self.start) + self.start

        if self.anim.done:
            entity.components.remove(self)
            entity.state.padding.left += value * (self.end - self.start) + self.start # type: ignore
            entity.state.padding.right += value * (self.end - self.start) + self.start # type: ignore
            entity.state.padding.top += value * (self.end - self.start) + self.start # type: ignore
            entity.state.padding.bottom += value * (self.end - self.start) + self.start # type: ignore

class ChangeSize(Component):
    def create(self, entity):
        self.entity = entity
        entity.canvas.tag_bind(entity.id, '<Button-1>', self.click, add='+')

    def click(self, e):
        if self.entity.state.size.width == 200:
            self.entity.state.size.width = 100
        else:
            self.entity.state.size.width = 200

class ChangeColor(Component):
    def create(self, entity):
        self.entity = entity
        entity.canvas.tag_bind(entity.id, '<Button-1>', self.click, add='+')

    def click(self, e):
        if self.entity.state.fill == Color.yellow():
            self.entity.state.fill = Color.gray()
        else:
            self.entity.state.fill = Color.yellow()

class EntitySwitcherState:
    def __init__(self, current: int = 0):
        self.current = current

    def copy(self):
        return copy.copy(self)


class EntitySwitcher(Entity):
    state: EntitySwitcherState

    def __init__(self, *, tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 current: int = 0,
                 components: list[Component] = [],
                 entities: list[Entity]):
        super().__init__(tag=tag, position=position, components=components)
        self.state = EntitySwitcherState(current=current)
        self.last_curr = current
        self._state = self.state.copy()
        self.entities = entities
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas
        for component in self.components:
            component.create(self)

        self.entities[self.state.current].create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)

        self.entities[self.state.current].destroy()

    def paint(self, ctx: FrameContext, position: Position):
        for component in self.components:
            component.before_paint(self, ctx, position, self._size, self._state)

        if self._state.current != self.last_curr:
            curr = self.entities[self.state.current]
            last = self.entities[self.last_curr]
            curr.create(self.canvas)
            self.canvas.tag_raise(curr.id, last.id)
            last.destroy()
            self.last_curr = self.state.current

        self.entities[self._state.current].paint(ctx, position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        child_size = self.entities[state.current].layout(ctx, constraints)
        self.entities[state.current]._size = child_size

        return child_size

class SwitchOnClick(Component):
    def create(self, entity):
        self.entity = entity
        entity.canvas.bind('<Button-1>', self.click)

    def click(self, e):
        self.entity.state.current = (self.entity.state.current + 1) % len(self.entity.entities)

scene = RootScene(
        children=[
            ScreenSizeLayout(
                    child=Padding(
                        padding=EdgeInset.all(20),
                        child=Center(
                            # child=Sprite(
                            #     size=Size(width=400, height=400),
                            #     components=[
                            #         DebugBounds()
                            #         ],
                            #     asset_key="hero2"
                            #     )
                            child=Rect(
                                fill=Color.from_hex('#ADD8E6'),
                                )
                            )
                        )
                    ),
            ScreenSizeLayout(
                child=Padding(
                    padding=EdgeInset.all(40),
                    child=Scene(
                        children=[
                            EntitySwitcher(
                                components=[
                                    SwitchOnClick()
                                    ],
                                entities=[
                                    Rect(
                                        size=Size(width=150, height=70),
                                        fill=Color.gray(),
                                        components=[
                                            PrintLifecycle(tag='rect1', before_paint=True),
                                            SquareShake(),
                                            PositionTransition(speed=100, skip=100),
                                            DebugBounds(color=Color.blue()),
                                            ],
                                        ),
                                    Rect(
                                        position=Position(x=100, y=150),
                                        size=Size(width=150, height=70),
                                        fill=Color.red(),
                                        components=[
                                            SquareShake(),
                                            PositionTransition(duration=.1)
                                            ],
                                        ),
                                    ]
                                )
                            ]
                        )
                    )
                ),
            ScreenSizeLayout(
                child=Padding(
                    padding=EdgeInset.all(40),
                    child=Flex(
                        direction=FlexDirection.Row,
                        children=[
                            Expanded(),
                            Rect(
                                size=Size(width=150, height=70),
                                fill=Color.gray(),
                                components=[
                                    ChangeSize(),
                                    ChangeColor(),
                                    FillTransition(duration=.3),
                                    SizeLayoutTransition(speed=100),
                                    ]
                                ),
                            Rect(
                                size=Size(width=150, height=70),
                                fill=Color.red(),
                                ),
                            Expanded(),
                            ]
                        )
                    )
                ),
            ScreenSizeLayout(
                child=Padding(
                    components=[
                        PaddingEffect(start=0, end=20, duration=1, repeat_times=3)
                        ],
                    padding=EdgeInset.all(20),
                    child=Scene(
                        children=[
                                Rect(
                                    fill=Color.white(),
                                    size=Size(width=100, height=50),
                                    child=Padding(
                                        padding=EdgeInset.all(10),
                                        child=Flex(
                                            direction=FlexDirection.Column,
                                            children=[
                                                Text(
                                                    components=[
                                                        FpsCounter(),
                                                        DebugBounds()
                                                        ],
                                                    text=""
                                                    ),
                                                Text(
                                                    components=[
                                                        AssetLoaderStats(),
                                                        ],
                                                    text=''
                                                    ),
                                                ]
                                            ),
                                        ),
                                ),
                            ]
                        ),
                    )
                ),
            ]
        )

game = Game(800, 600, scene)
game.asset_manager.register('hero', Asset(AssetType.Still, 'assets/hero.png'))
game.asset_manager.register('hero2', Asset(AssetType.Still, 'assets/hero.jpg'))
game.asset_manager.register('small', Asset(AssetType.Still, 'assets/small.png', Resampling.NEAREST))

