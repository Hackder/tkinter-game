from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from tkinter import Canvas

from engine.models import FrameContext, Position, Size, DefinedSize, Constraints
from engine.entities.effects import Effect, LayoutEffect

class Component(ABC):
    @abstractmethod
    def create(self, entity: Entity):
        pass

class Entity(ABC):
    @abstractmethod
    def __init__(self, *,
                 tag: str|None,
                 position: Position,
                 effects: list[Effect],
                 layout_effects: list[LayoutEffect],
                 components: list[Component] = []
                 ):
        self.id = 0
        self.tag = tag
        self.position = position
        self.effects = effects
        self.layout_effects = layout_effects
        self.components = components
        self._size = DefinedSize(width=0, height=0)

    @abstractmethod
    def create(self, canvas: Canvas):
        pass

    @abstractmethod
    def destroy(self):
        pass

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

    def create(self, canvas: Canvas):
        self.canvas = canvas
        for child in self.children:
            child.create(canvas)

    def destroy(self):
        for child in self.children:
            child.destroy()

    def paint(self, ctx: FrameContext):
        for child in self.children:
            child.paint(ctx, self.position)

    def layout(self, ctx: FrameContext):
        constraints = Constraints(min_width=0, min_height=0, max_width=ctx.width, max_height=ctx.height)

        for child in self.children:
            child.layout(ctx, constraints)

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
                 fill: str = 'red',
                 outline: str = 'black',
                 outline_width: float = 1.0,
                 effects: list[Effect] = [],
                 layout_effects: list[LayoutEffect] = [],
                 child: Entity|None = None,
                 ):
        super().__init__(tag=tag, position=position, effects=effects, layout_effects=layout_effects)
        self.state = RectState(size=size, fill=fill, outline=outline, outline_width=outline_width)
        self._state = self.state.copy()
        self.child = child

    def create(self, canvas: Canvas):
        self.canvas = canvas
        self.id = canvas.create_rectangle(0, 0, 0, 0)

        for component in self.components:
            component.create(self)

        if self.child is not None:
            self.child.create(canvas)

    def destroy(self):
        self.canvas.delete(self.id)
        if self.child is not None:
            self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)
        size = self._size.copy()

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

