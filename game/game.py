from engine.animation.utils import Animation, AnimationDirection, AnimationEnd, Easing
from engine.debug.entities import FpsCounter
from engine.entities.basic import Rect, RootScene
from engine.entities.effects import LayoutEffect, PositionTransition, SquareShake
from engine.entities.layout import Center, ScreenSizeLayout, Padding, PaddingSize, Stack
from engine.models import Size, Position
from engine.game import Game

class PaddingEffect(LayoutEffect):
    def __init__(self, *, start: float, end: float, duration: float, repeat_times: int = 0):
        self.start = start
        self.end = end
        self.anim = Animation(duration=duration, direction=AnimationDirection.Alternate, repeat_times=repeat_times, end=AnimationEnd.End)

    def process(self, entity, ctx, state):
        value = self.anim.process(ctx.delta_time)

        state.padding.left += value * (self.end - self.start) + self.start
        state.padding.right += value * (self.end - self.start) + self.start
        state.padding.top += value * (self.end - self.start) + self.start
        state.padding.bottom += value * (self.end - self.start) + self.start

        if self.anim.done:
            entity.layout_effects.remove(self)
            entity.state.padding.left += value * (self.end - self.start) + self.start # type: ignore
            entity.state.padding.right += value * (self.end - self.start) + self.start # type: ignore
            entity.state.padding.top += value * (self.end - self.start) + self.start # type: ignore
            entity.state.padding.bottom += value * (self.end - self.start) + self.start # type: ignore

scene = RootScene(
        children=[
            ScreenSizeLayout(
                child=Center(
                    child=Stack(
                        children=[
                            Rect(
                                size=Size(width=150, height=70),
                                fill='gray',
                                effects=[
                                    SquareShake(),
                                    PositionTransition(speed=100)
                                    ],
                                ),
                            Rect(
                                position=Position(x=100, y=150),
                                size=Size(width=150, height=70),
                                fill='red',
                                effects=[
                                    SquareShake(),
                                    PositionTransition(speed=100)
                                    ],
                                ),
                            ]
                        )
                    )
                ),
            ScreenSizeLayout(
                child=Padding(
                    padding=PaddingSize.all(20),
                    child=FpsCounter()
                    )
                )
            ]
        )

game = Game(800, 600, scene)

def click(e):
    game.scene.children[0].child.child.children[0].position.x = 100

game.canvas.bind('<Button-1>', click)
