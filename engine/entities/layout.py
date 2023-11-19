import copy
from tkinter import Canvas

from engine.entities.effects import Effect, LayoutEffect
from engine.models import FrameContext, DefinedSize, Constraints, Position
from engine.entities.basic import Entity

class ScreenSizeLayout(Entity):
    def __init__(self, *,
                 tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 effects: list[Effect] = [],
                 child: Entity,
                 ):
        super().__init__(tag=tag, position=position, effects=effects, layout_effects=[])
        self.child = child

    def construct(self, canvas: Canvas):
        self.canvas = canvas
        self.child.construct(canvas)

    def paint(self, ctx: FrameContext, position: Position):
        self.child.paint(ctx, position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> DefinedSize:
        constraints = Constraints(min_width=0, min_height=0, max_width=ctx.width, max_height=ctx.height)

        self.child._size = self.child.layout(ctx, constraints)

        return self.child._size

class PaddingSize:
    def __init__(self, top: float, right: float, bottom: float, left: float):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    @staticmethod
    def all(value: float):
        return PaddingSize(top=value, right=value, bottom=value, left=value)

class PaddingState:
    def __init__(self, padding: PaddingSize):
        self.padding = padding

    def copy(self):
        return copy.deepcopy(self)

class Padding(Entity):
    def __init__(self, *,
                 tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 effects: list[Effect] = [],
                 padding: PaddingSize,
                 layout_effects: list[LayoutEffect] = [],
                 child: Entity,
                 ):
        super().__init__(tag=tag, position=position, effects=effects, layout_effects=layout_effects)
        self.child = child
        self.state = PaddingState(padding=padding)
        self._state = self.state.copy()
        self._size = DefinedSize(width=0, height=0)

    def construct(self, canvas: Canvas):
        self.canvas = canvas
        self.child.construct(canvas)

    def paint(self, ctx: FrameContext, position: Position):
        for effect in self.effects:
            effect.process(ctx, position, self._size, self._state)

        child_position = Position(x=position.x + self._state.padding.left, y=position.y + self._state.padding.top)
        self.child.paint(ctx, child_position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> DefinedSize:
        state = self.state.copy()
        for effect in self.layout_effects:
            effect.process(ctx, state)
        self._state = state

        c = constraints.copy()
        x_padding = state.padding.left + state.padding.right
        y_padding = state.padding.top + state.padding.bottom

        if c.max_width is None or c.max_height is None:
            raise ValueError("Cannot apply padding to unbounded constraints")

        c.min_width -= x_padding
        c.max_width -= x_padding
        c.min_height -= y_padding
        c.max_height -= y_padding

        self.child._size = self.child.layout(ctx, c)

        return constraints.to_max_defined_size()

class Center(Entity):
    def __init__(self, *,
                 tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 effects: list[Effect] = [],
                 child: Entity,
                 ):
        super().__init__(tag=tag, position=position, effects=effects, layout_effects=[])
        self.child = child
    
    def construct(self, canvas: Canvas):
        self.canvas = canvas
        self.child.construct(canvas)

    def paint(self, ctx: FrameContext, position: Position):
        for effect in self.effects:
            effect.process(ctx, position, self._size, None)

        child_position = Position(x=position.x + (self._size.width - self.child._size.width) / 2,
                                  y=position.y + (self._size.height - self.child._size.height) / 2)
        
        self.child.paint(ctx, child_position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> DefinedSize:
        self.child._size = self.child.layout(ctx, constraints)

        return constraints.to_max_defined_size()

