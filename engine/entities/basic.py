from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from tkinter import Canvas
from typing import Any
from engine.assets import AssetManader

from engine.models import Color, FrameContext, Position, Size, Constraints
from engine.entities.components.base import Component


class Entity(ABC):
    state: Any
    canvas: Canvas

    @abstractmethod
    def __init__(self, *,
                 tag: str|None,
                 position: Position,
                 components: list[Component] = []
                 ):
        self.id = 0
        self.tag = tag
        self.position = position
        self.components = components
        self._size = Size(width=0, height=0)

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
    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(tag={self.tag}, id={self.id})"


class RootScene:
    def __init__(self, *,
                 position: Position = Position(x=0, y=0),
                 children: list[Entity] = [],
                 ):
        self.position = position
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
    def __init__(self, *, size: Size | None, fill: Color, outline: Color, outline_width: float):
        self.size = size
        self.fill = fill
        self.outline = outline
        self.outline_width = outline_width

    def copy(self):
        return copy.deepcopy(self)

    def __repr__(self):
        return f"RectState(size={self.size}, fill={self.fill}, outline={self.outline}, outline_width={self.outline_width})"

class Rect(Entity):
    state: RectState

    def __init__(self, *,
                 tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 size: Size | None = None,
                 fill: Color = Color.white(),
                 outline: Color = Color.black(),
                 outline_width: float = 1.0,
                 components: list[Component] = [],
                 child: Entity|None = None,
                 ):
        super().__init__(tag=tag, position=position, components=components)
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
        for component in self.components:
            component.destroy(self)
        self.canvas.delete(self.id)
        if self.child is not None:
            self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)
        size = self._size.copy()

        for effect in self.components:
            effect.before_paint(self, ctx, pos, size, self._state)
        
        self.canvas.coords(self.id, pos.x, pos.y, pos.x + size.width, pos.y + size.height)
        self.canvas.itemconfigure(self.id,
                                  fill=self._state.fill.to_hex(),
                                  outline=self._state.outline.to_hex(),
                                  width=self._state.outline_width)

        if self.child is not None:
            self.child.paint(ctx, pos)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        if self.child is not None:
            self.child._size = self.child.layout(ctx, constraints.limit(self.state.size))
            if state.size is not None:
                size = Size(
                        width=max(state.size.width, self.child._size.width),
                        height=max(state.size.height, self.child._size.height)
                        )
            else:
                size = self.child._size.copy()

            return constraints.fit_size(size)

        return constraints.fit_size(state.size)

class TextState:
    def __init__(self, *, text: str, width: float|None, fill: Color):
        self.text = text
        self.width = width
        self.fill = fill

    def copy(self):
        return copy.deepcopy(self)

class Text(Entity):
    def __init__(self, *, tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 text: str,
                 width: float|None = None,
                 fill: Color = Color.black(),
                 components: list[Component] = []
                 ):
        super().__init__(tag=tag, position=position, components=components)
        self.state = TextState(text=text, width=width, fill=fill)
        self._state = self.state.copy()
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas
        self.id = canvas.create_text(0, 0, text='', anchor='nw')

        for component in self.components:
            component.create(self)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.canvas.delete(self.id)

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)

        for effect in self.components:
            effect.before_paint(self, ctx, pos, self._size, self._state)

        self.canvas.coords(self.id, pos.x, pos.y)
        self.canvas.itemconfigure(self.id,
                                  text=self._state.text,
                                  fill=self._state.fill.to_hex(),
                                  width=self._size.width)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        self.canvas.itemconfigure(self.id, text=state.text, fill=state.fill.to_hex(), width=None)
        bbox = self.canvas.bbox(self.id)

        w = constraints.fit_width(bbox[2] - bbox[0] + 6)
        h = constraints.fit_height(bbox[3] - bbox[1])

        self._size = Size(width=w, height=h)

        return self._size

class SpriteState:
    def __init__(self, *, asset_key: str, size: Size | None = None):
        self.asset_key = asset_key
        self.size = size

    def copy(self):
        return copy.deepcopy(self)

class Sprite(Entity):
    state: SpriteState

    def __init__(self, *, tag: str|None = None,
                 position: Position = Position(x=0, y=0),
                 size: Size | None = None,
                 asset_key: str,
                 components: list[Component] = []
                 ):
        super().__init__(tag=tag, position=position, components=components)
        self.state = SpriteState(asset_key=asset_key, size=size)
        self._state = self.state.copy()
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas
        self.id = canvas.create_image(0, 0, image='', anchor='nw')

        for component in self.components:
            component.create(self)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.canvas.delete(self.id)

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)

        for effect in self.components:
            effect.before_paint(self, ctx, pos, self._size, self._state)
        
        asset = ctx.asset_manager.get(self._state.asset_key, self._size.width, self._size.height)
        self.canvas.coords(self.id, pos.x, pos.y)
        self.canvas.itemconfigure(self.id, image=asset)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        return constraints.fit_size(state.size)
