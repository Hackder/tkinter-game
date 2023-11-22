from engine.animation.utils import Animation, AnimationDirection, AnimationEnd, Easing
from engine.entities.basic import Rect, RootScene, Text
from engine.entities.components.base import Component
from engine.entities.components.debug import DebugBounds, FpsCounter
from engine.entities.components.effects import PositionTransition, SquareShake, SizeLayoutTransition
from engine.entities.layout import Center, Flex, FlexDirection, ScreenSizeLayout, Padding, EdgeInset, Stack, Expanded
from engine.models import Size, Position
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
        entity.canvas.tag_bind(entity.id, '<Button-1>', self.click)

    def click(self, e):
        if self.entity.state.size.width == 200:
            self.entity.state.size.width = 100
        else:
            self.entity.state.size.width = 200

scene = RootScene(
        children=[
            ScreenSizeLayout(
                child=Center(
                    child=Stack(
                        children=[
                            Rect(
                                size=Size(width=150, height=70),
                                fill='gray',
                                components=[
                                    SquareShake(),
                                    PositionTransition(speed=100, skip=100)
                                    ],
                                ),
                            Rect(
                                position=Position(x=100, y=150),
                                size=Size(width=150, height=70),
                                fill='red',
                                components=[
                                    SquareShake(),
                                    PositionTransition(duration=.1)
                                    ],
                                ),
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
                                fill='gray',
                                components=[
                                    ChangeSize(),
                                    SizeLayoutTransition(speed=100),
                                    ]
                                ),
                            Rect(
                                size=Size(width=150, height=70),
                                fill='red',
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
                    child=Stack(
                        children=[Text(
                        components=[
                            FpsCounter(),
                            DebugBounds()
                            ],
                        text="Hello world"
                        )]
                        ),
                    )
                )
            ]
        )

game = Game(800, 600, scene)

