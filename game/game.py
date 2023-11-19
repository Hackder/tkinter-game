from engine.animation.utils import Animation, AnimationDirection
from engine.debug.entities import FpsCounter
from engine.entities.basic import Rect, RootScene
from engine.entities.effects import LayoutEffect
from engine.entities.layout import Center, ScreenSizeLayout, Padding, PaddingSize
from engine.models import Size
from engine.renderer import Renderer

class PaddingEffect(LayoutEffect):
    def __init__(self, start: float, end: float, duration: float):
        self.start = start
        self.end = end
        self.anim = Animation(duration=duration, direction=AnimationDirection.Normal)


    def process(self, ctx, state):
        value = self.anim.process(ctx.delta_time)
        print(value)
        state.padding.left += value * (self.end - self.start) + self.start
        state.padding.right += value * (self.end - self.start) + self.start
        state.padding.top += value * (self.end - self.start) + self.start
        state.padding.bottom += value * (self.end - self.start) + self.start


scene = RootScene(
        children=[
            ScreenSizeLayout(
                child=Padding(
                    padding=PaddingSize.all(10),
                    layout_effects=[
                        PaddingEffect(-5, 30, 1)
                        ],
                    child=Rect(size=Size(width=100, height=100))
                    )
                ),
            ScreenSizeLayout(
                child=Center(
                    child=FpsCounter()
                    )
                )
            ]
        )

renderer = Renderer(800, 600, scene)
