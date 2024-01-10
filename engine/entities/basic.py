from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from tkinter import Canvas
from tkinter.font import Font
from typing import Any, Literal
from timeit import default_timer as timer
from engine.entities.state import EntityState
from engine.entities.types import BoundValue

from engine.models import Color, FrameContext, Position, Size, Constraints
from engine.entities.components.base import Component


class Entity(ABC):
    state: Any
    canvas: Canvas

    @abstractmethod
    def __init__(self, *, tag: str | None, components: list[Component] = []):
        self.id = 0
        self.tag = tag
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
    def __init__(
        self,
        *,
        children: list[Entity] = [],
    ):
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
            child.paint(ctx, Position.zero())

    def layout(self, ctx: FrameContext):
        constraints = Constraints(
            min_width=0, min_height=0, max_width=ctx.width, max_height=ctx.height
        )

        for child in self.children:
            child.layout(ctx, constraints)


class RectState:
    def __init__(
        self, *, size: Size | None, fill: Color, outline: Color, outline_width: float
    ):
        self.size = size
        self.fill = fill
        self.outline = outline
        self.outline_width = outline_width

    def copy(self):
        return copy.copy(self)

    def __repr__(self):
        return f"RectState(size={self.size}, fill={self.fill}, outline={self.outline}, outline_width={self.outline_width})"


class Rect(Entity):
    state: RectState

    def __init__(
        self,
        *,
        tag: str | None = None,
        size: Size | None = None,
        fill: Color = Color.white(),
        outline: Color = Color.black(),
        outline_width: float = 1.0,
        components: list[Component] = [],
        child: Entity | None = None,
    ):
        super().__init__(tag=tag, components=components)
        self.state = RectState(
            size=size, fill=fill, outline=outline, outline_width=outline_width
        )
        self._state = self.state.copy()
        self.child = child

    def create(self, canvas: Canvas):
        self.canvas = canvas
        tags = [self.tag] if self.tag is not None else []
        self.id = canvas.create_rectangle(0, 0, 0, 0, tags=tags)

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
        pos = position.copy()
        size = self._size.copy()

        self.canvas.tag_raise(self.id)
        for effect in self.components:
            effect.before_paint(self, ctx, pos, size, self._state)

        self.canvas.coords(
            self.id, pos.x, pos.y, pos.x + size.width, pos.y + size.height
        )
        self.canvas.itemconfigure(
            self.id,
            fill=self._state.fill.to_hex(),
            outline=self._state.outline.to_hex(),
            width=self._state.outline_width,
        )

        if self.child is not None:
            self.child.paint(ctx, pos)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        if self.child is not None:
            new_constraints = constraints.limit(state.size)
            self.child._size = self.child.layout(
                ctx,
                new_constraints.force_max() if state.size is not None else constraints,
            )
            if state.size is not None:
                size = Size(
                    width=max(state.size.width, self.child._size.width),
                    height=max(state.size.height, self.child._size.height),
                )
            else:
                size = self.child._size.copy()

            return constraints.fit_size(size)

        return constraints.fit_size(state.size)


class PureRect(Entity):
    state: RectState

    def __init__(
        self,
        *,
        tag: str | None = None,
        size: Size | None = None,
        fill: Color = Color.white(),
        outline: Color = Color.black(),
        outline_width: float = 1.0,
        position: Position = Position.zero(),
        components: list[Component] = [],
        child: Entity | None = None,
    ):
        if len(components) > 0:
            raise ValueError("PureRect cannot have components")
        super().__init__(tag=tag, components=components)
        self.state = RectState(
            size=size, fill=fill, outline=outline, outline_width=outline_width
        )
        self._state = self.state.copy()
        self.child = child
        self.position = position

    def create(self, canvas: Canvas):
        self.canvas = canvas
        tags = [self.tag] if self.tag is not None else []
        self.id = canvas.create_rectangle(0, 0, 0, 0, tags=tags)

        if self.child is not None:
            self.child.create(canvas)

    def destroy(self):
        self.canvas.delete(self.id)
        if self.child is not None:
            self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        self.canvas.tag_raise(self.id)

        self.canvas.coords(
            self.id,
            position.x + self.position.x,
            position.y + self.position.y,
            position.x + self.position.x + self._size.width,
            position.y + self.position.y + self._size.height,
        )
        self.canvas.itemconfigure(
            self.id,
            fill=self._state.fill.to_hex(),
            outline=self._state.outline.to_hex(),
            width=self._state.outline_width,
        )

        if self.child is not None:
            self.child.paint(ctx, position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        if self.child is not None:
            new_constraints = constraints.limit(self.state.size)
            self.child._size = self.child.layout(
                ctx,
                new_constraints.force_max()
                if self.state.size is not None
                else constraints,
            )
            if self.state.size is not None:
                size = Size(
                    width=max(self.state.size.width, self.child._size.width),
                    height=max(self.state.size.height, self.child._size.height),
                )
            else:
                size = self.child._size.copy()

            return constraints.fit_size(size)

        return constraints.fit_size(self.state.size)


class TextState(EntityState):
    justify: Literal["left", "center", "right"]

    def __init__(
        self,
        *,
        text: BoundValue[str],
        width: float | None,
        fill: Color,
        font: Font,
        justify: Literal["left", "center", "right"],
    ):
        self._bound_text = text
        self.text = text()
        self.width = width
        self.fill = fill
        self.font = font
        self.justify = justify

    def copy(self):
        return copy.copy(self)


class Text(Entity):
    state: TextState
    _state: TextState

    def __init__(
        self,
        *,
        tag: str | None = None,
        text: BoundValue[str],
        width: float | None = None,
        fill: Color = Color.black(),
        font: Font | None = None,
        justify: Literal["left", "center", "right"] = "left",
        components: list[Component] = [],
    ):
        super().__init__(tag=tag, components=components)
        f = font if font is not None else Font(family="Helvetica", size=12)
        self.state = TextState(
            text=text, width=width, fill=fill, font=f, justify=justify
        )
        self._state = self.state.copy()
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas
        tags = [self.tag] if self.tag is not None else []
        self.id = canvas.create_text(0, 0, text="", anchor="nw", tags=tags)

        for component in self.components:
            component.create(self)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.canvas.delete(self.id)

    def paint(self, ctx: FrameContext, position: Position):
        pos = position.copy()

        self.canvas.tag_raise(self.id)
        for effect in self.components:
            effect.before_paint(self, ctx, pos, self._size, self._state)

        self.canvas.coords(self.id, pos.x, pos.y)
        self.canvas.itemconfigure(
            self.id,
            text=self._state.text,
            fill=self._state.fill.to_hex(),
            width=self._size.width,
            font=self._state.font,
            justify=self._state.justify,
        )

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        self.state.update()
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        text_width = self._state.font.measure(state.text)
        w = constraints.fit_width(text_width)

        self.canvas.itemconfigure(
            self.id, text=state.text, fill=state.fill.to_hex(), width=w, font=state.font
        )
        bbox = self.canvas.bbox(self.id)
        if bbox is None:
            bbox = self.last_bbox
        self.last_bbox = bbox

        h = constraints.fit_height(bbox[3] - bbox[1])

        self._size = Size(width=w, height=h)

        return self._size


class SpriteState:
    def __init__(self, *, asset_key: str, size: Size | None = None):
        self.asset_key = asset_key
        self.size = size

    def copy(self):
        return copy.copy(self)


class Sprite(Entity):
    state: SpriteState

    def __init__(
        self,
        *,
        tag: str | None = None,
        size: Size | None = None,
        asset_key: str,
        components: list[Component] = [],
    ):
        super().__init__(tag=tag, components=components)
        self.state = SpriteState(asset_key=asset_key, size=size)
        self._state = self.state.copy()
        self._size = Size(width=10, height=10)

    def create(self, canvas: Canvas):
        self.canvas = canvas
        self.id = canvas.create_image(0, 0, image="", anchor="nw")

        for component in self.components:
            component.create(self)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.canvas.delete(self.id)

    def paint(self, ctx: FrameContext, position: Position):
        pos = position.copy()

        self.canvas.tag_raise(self.id)
        for effect in self.components:
            effect.before_paint(self, ctx, pos, self._size, self._state)

        asset = ctx.asset_manager.get(
            self._state.asset_key, int(self._size.width), int(self._size.height)
        )
        self.canvas.coords(self.id, pos.x, pos.y)
        self.canvas.itemconfigure(self.id, image=asset)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        return constraints.fit_size(state.size)


class AnimatedSpriteState(EntityState):
    def __init__(
        self,
        *,
        paused: BoundValue[bool],
        asset_key: BoundValue[str],
        size: Size | None = None,
        speed: float = 1.0,
    ):
        self._bound_paused = paused
        self.paused = paused()
        self._bound_asset_key = asset_key
        self.asset_key = asset_key()
        self.size = size
        self.speed = speed
        self.frame_idx = 0
        self.frame_time = timer()

    def copy(self):
        return copy.copy(self)


class AnimatedSprite(Entity):
    state: AnimatedSpriteState

    def __init__(
        self,
        *,
        tag: str | None = None,
        size: Size | None = None,
        asset_key: BoundValue[str],
        paused: BoundValue[bool] = lambda: False,
        components: list[Component] = [],
    ):
        super().__init__(tag=tag, components=components)
        self.state = AnimatedSpriteState(asset_key=asset_key, size=size, paused=paused)
        self._state = self.state.copy()
        self._size = Size(width=10, height=10)

    def set_asset_key(self, asset_key: str):
        if self.state.asset_key == asset_key:
            return
        self.state.asset_key = asset_key
        self.state.frame_idx = 0
        self.state.frame_time = timer()

    def create(self, canvas: Canvas):
        self.canvas = canvas
        self.id = canvas.create_image(0, 0, image="", anchor="nw", tags=[self.tag])

        for component in self.components:
            component.create(self)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.canvas.delete(self.id)

    def paint(self, ctx: FrameContext, position: Position):
        pos = position.copy()

        self.canvas.tag_raise(self.id)
        for effect in self.components:
            effect.before_paint(self, ctx, pos, self._size, self._state)

        asset_list = ctx.asset_manager.get_animated(
            self._state.asset_key, int(self._size.width), int(self._size.height)
        )
        raw_asset = ctx.asset_manager.get_raw(self._state.asset_key)

        asset = None
        if (
            asset_list is not None
            and raw_asset is not None
            and raw_asset.animation is not None
        ):
            now = timer()
            if (
                now - self._state.frame_time
                > self._state.speed * (1 / raw_asset.animation.fps)
                and not self._state.paused
            ):
                self.state.frame_idx += 1
                self.state.frame_time = now

            self.state.frame_idx %= len(asset_list)
            asset = asset_list[self.state.frame_idx]

        self.canvas.coords(self.id, pos.x, pos.y)
        self.canvas.itemconfigure(self.id, image=asset)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        self.state.update()
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        self._state = state

        return constraints.fit_size(state.size)
