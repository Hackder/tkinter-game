import copy
from abc import ABC, abstractmethod
from tkinter import Canvas

from engine.models import FrameContext, Position, Size, DefinedSize, Constraints
from engine.entities.effects import Effect, LayoutEffect


class Entity(ABC):
    id = 0
    _size: DefinedSize = DefinedSize(width=0, height=0)

    @abstractmethod
    def __init__(self, *,
                 tag: str|None,
                 position: Position,
                 effects: list[Effect],
                 layout_effects: list[LayoutEffect],
                 ):
        self.tag = tag
        self.position = position
        self.effects = effects
        self.layout_effects = layout_effects
        self.flex = 0

    @abstractmethod
    def construct(self, canvas: Canvas):
        self.canvas = canvas

    @abstractmethod
    def paint(self, ctx: FrameContext, position: Position):
        pass

    @abstractmethod
    def layout(self, ctx: FrameContext, constraints: Constraints) -> DefinedSize:
        pass


class RootScene:
    def __init__(self, *,
                 position: Position = Position(x=0, y=0),
                 effects: list[Effect] = [],
                 children: list[Entity] = [],
                 ):
        self.position = position
        self.effects = effects
        self.children = children

    def construct(self, canvas: Canvas):
        self.canvas = canvas
        for child in self.children:
            child.construct(canvas)

    def paint(self, ctx: FrameContext):
        for child in self.children:
            child.paint(ctx, self.position)

    def layout(self, ctx: FrameContext):
        for child in self.children:
            child.layout(ctx, Constraints.unbounded())

class RectState:
    def __init__(self, *, size: Size, fill: str, outline: str, outline_width: float):
        self.size = size
        self.fill = fill
        self.outline = outline
        self.outline_width = outline_width

    def copy(self):
        return copy.deepcopy(self)

class Rect(Entity):
    def __init__(self, *,
                 tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 size: Size = Size.unbounded(),
                 fill: str = 'black',
                 outline: str = 'red',
                 outline_width: float = 1.0,
                 effects: list[Effect] = [],
                 layout_effects: list[LayoutEffect] = [],
                 child: Entity|None = None,
                 ):
        super().__init__(tag=tag, position=position, effects=effects, layout_effects=layout_effects)
        self.state = RectState(size=size, fill=fill, outline=outline, outline_width=outline_width)
        self._state = self.state.copy()
        self.child = child

    def construct(self, canvas: Canvas):
        self.canvas = canvas
        self.id = canvas.create_rectangle(0, 0, 0, 0)
        if self.child is not None:
            self.child.construct(canvas)

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)
        size = self._size

        for effect in self.effects:
            effect.process(self, ctx, pos, size, None)
        
        self.canvas.coords(self.id, pos.x, pos.y, pos.x + size.width, pos.y + size.height)
        self.canvas.itemconfigure(self.id, fill=self._state.fill, outline=self._state.outline, width=self._state.outline_width)

        if self.child is not None:
            self.child.paint(ctx, pos)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> DefinedSize:
        state = self.state.copy()
        for effect in self.layout_effects:
            effect.process(self, ctx, state)

        self._state = state

        if self.child is not None:
            self.child._size = self.child.layout(ctx, constraints.limit(self.state.size))
            size = Size(
                    width=max(state.size.width, self.child._size.width) if state.size.width is not None else self.child._size.width,
                    height=max(state.size.height, self.child._size.height) if state.size.height is not None else self.child._size.height
                    )
            return constraints.fit_size(size)

        return constraints.fit_size(state.size)

