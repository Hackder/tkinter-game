import copy
from tkinter import Canvas
from timeit import default_timer as timer
from engine.entities.effects import Effect, LayoutEffect

from engine.models import FrameContext, DefinedSize, Constraints, Position
from engine.entities.basic import Entity

class FpsCounterState:
    def __init__(self, fps: float, width: float|None, period: int):
        self.fps = fps
        self.width = width
        self.period = period

    def copy(self):
        return copy.deepcopy(self)

class FpsCounter(Entity):
    def __init__(self, *,
                 tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 period: int = 10,
                 width: float|None=None,
                 effects: list[Effect] = [],
                 layout_effects: list[LayoutEffect] = []):
        super().__init__(tag=tag, position=position, effects=effects, layout_effects=layout_effects)
        self.state = FpsCounterState(0, width, period)
        self._state = self.state.copy()
        self.last_check = timer()
        self.iter = 0

    def construct(self, canvas: Canvas):
        self.canvas = canvas
        self.id = canvas.create_text(0, 0, text='0', anchor='nw', justify='left', fill="black")

    def update(self):
        if self.iter < self.state.period:
            self.iter += 1
            return self.state.fps

        self.iter = 1
        now = timer()
        self.state.fps = self.state.period / (now - self.last_check)
        self.last_check = now
        return self.state.fps

    def paint(self, ctx: FrameContext, position: Position):
        for effect in self.effects:
            effect.process(ctx, position, self._size, self._state)

        self.canvas.itemconfigure(self.id, text=f'{self._state.fps:.2f} fps', width=self._size.width)
        self.canvas.coords(self.id, position.x, position.y)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> DefinedSize:
        self.update()

        state = self.state.copy()

        for effect in self.layout_effects:
            effect.process(ctx, state)

        self._state = state

        w = constraints.fit_width(state.width)

        self.canvas.itemconfigure(self.id, width=w)

        bbox = self.canvas.bbox(self.id)

        w = bbox[2] - bbox[0] + 5
        h = bbox[3] - bbox[1]

        return DefinedSize(width=w, height=h)

