import copy
from tkinter import Canvas
from enum import StrEnum

from engine.entities.components.base import Component
from engine.models import FrameContext, Size, Constraints, Position, EdgeInset
from engine.entities.basic import Entity
from engine.threed.entities.basic import Entity3d
from engine.threed.models import Camera, Position3d, Quaternion


class ScreenSizeLayout(Entity):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        components: list[Component] = [],
        child: Entity,
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.child = child

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        self.child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        self.child.paint(ctx, position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        constraints = Constraints(
            min_width=ctx.width,
            min_height=ctx.height,
            max_width=ctx.width,
            max_height=ctx.height,
        )

        self.child._size = self.child.layout(ctx, constraints)

        return Size(width=ctx.width, height=ctx.height)


class PaddingState:
    def __init__(self, padding: EdgeInset):
        self.padding = padding

    def copy(self):
        return copy.deepcopy(self)


class Padding(Entity):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        padding: EdgeInset,
        components: list[Component] = [],
        child: Entity,
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.child = child
        self.state = PaddingState(padding=padding)
        self._state = self.state.copy()
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        self.child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = position.add(self.position)

        for component in self.components:
            component.before_paint(self, ctx, pos, self._size, self._state)

        child_position = Position(
            x=pos.x + self._state.padding.left, y=pos.y + self._state.padding.top
        )
        self.child.paint(ctx, child_position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)
        self._state = state

        c = constraints.copy()
        x_padding = state.padding.left + state.padding.right
        y_padding = state.padding.top + state.padding.bottom

        c.min_width = max(c.min_width - x_padding, 0)
        c.min_height = max(c.min_height - y_padding, 0)
        c.max_width = max(c.max_width - x_padding, 0)
        c.max_height = max(c.max_height - y_padding, 0)

        child_size = self.child.layout(ctx, c)
        self.child._size = child_size

        return constraints.fit_size(
            Size(
                width=child_size.width + x_padding, height=child_size.height + y_padding
            )
        )


class Center(Entity):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        components: list[Component] = [],
        child: Entity,
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.child = child

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        self.child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)

        for component in self.components:
            component.before_paint(self, ctx, pos, self._size, None)

        child_position = Position(
            x=pos.x + (self._size.width - self.child._size.width) / 2,
            y=pos.y + (self._size.height - self.child._size.height) / 2,
        )

        self.child.paint(ctx, child_position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        self.child._size = self.child.layout(ctx, constraints.with_min(0, 0))

        return constraints.fit_size(self.child._size)


class Stack(Entity):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        components: list[Component] = [],
        children: list[Entity] = [],
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.children = children

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        for child in self.children:
            child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        for child in self.children:
            child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)
        size = self._size.copy()

        for component in self.components:
            component.before_paint(self, ctx, pos, size, None)

        for child in self.children:
            child.paint(ctx, pos)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        constraints = constraints.force_max()

        for component in self.components:
            component.before_layout(self, ctx, None)

        for child in self.children:
            child._size = child.layout(ctx, constraints)

        return constraints.to_max_size()


class Scene(Entity):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        components: list[Component] = [],
        children: list[Entity] = [],
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.children = children

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        for child in self.children:
            child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        for child in self.children:
            child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)
        size = self._size.copy()

        for component in self.components:
            component.before_paint(self, ctx, pos, size, None)

        for child in self.children:
            child.paint(ctx, pos)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        constraints = constraints.with_min(0, 0)
        max_w = 0
        max_h = 0
        for child in self.children:
            child_size = child.layout(ctx, constraints)
            child._size = child_size
            max_w = max(max_w, child_size.width + child.position.x)
            max_h = max(max_h, child_size.height + child.position.y)

        return Size(width=max_w, height=max_h)


class FlexDirection(StrEnum):
    Row = "Row"
    Column = "Column"

    def __repr__(self):
        if self == FlexDirection.Row:
            return "Row"
        elif self == FlexDirection.Column:
            return "Column"


class Alignment(StrEnum):
    Start = "Start"
    Center = "Center"
    End = "End"
    Stretch = "Stretch"


class FlexState:
    def __init__(self, *, direction: FlexDirection, align: Alignment, gap: float):
        self.direction = direction
        self.align = align
        self.gap = gap

    def copy(self):
        return copy.deepcopy(self)


class Flex(Entity):
    state: FlexState

    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        direction: FlexDirection,
        align: Alignment = Alignment.Start,
        gap: float = 0,
        components: list[Component] = [],
        children: list[Entity] = [],
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.children = children
        self.state = FlexState(direction=direction, align=align, gap=gap)
        self._state = self.state.copy()

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        for child in self.children:
            child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        for child in self.children:
            child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)

        for component in self.components:
            component.before_paint(self, ctx, pos, self._size, self._state)

        for child in self.children:
            p = pos.copy()
            if self._state.direction == FlexDirection.Row:
                if self._state.align == Alignment.End:
                    p.y += self._size.height - child._size.height
                elif self._state.align == Alignment.Center:
                    p.y += (self._size.height - child._size.height) / 2
                child.paint(ctx, p)
                pos.x += child._size.width
                pos.x += self._state.gap
            else:
                if self._state.align == Alignment.End:
                    p.x += self._size.width - child._size.width
                elif self._state.align == Alignment.Center:
                    p.x += (self._size.width - child._size.width) / 2
                child.paint(ctx, p)
                pos.y += child._size.height
                pos.y += self._state.gap

    def is_flex_child(self, child: Entity) -> bool:
        return hasattr(child, "state") and hasattr(child.state, "flex") and child.state.flex != 0  # type: ignore

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        specific_children_size = 0
        flex_total = 0
        max_cross = 0
        orig_c = constraints.copy()

        if state.direction == FlexDirection.Row:
            if state.align != Alignment.Stretch:
                constraints.min_height = 0
            else:
                constraints.min_height = constraints.max_height
            constraints.min_width = 0
        else:
            if state.align != Alignment.Stretch:
                constraints.min_width = 0
            else:
                constraints.min_width = constraints.max_width
            constraints.min_height = 0

        for child in self.children:
            if self.is_flex_child(child):
                flex_total += child.state.flex  # type: ignore
                continue

            if state.direction == FlexDirection.Row:
                child._size = child.layout(ctx, constraints)
                specific_children_size += child._size.width
                max_cross = max(max_cross, child._size.height)
            else:
                child._size = child.layout(ctx, constraints)
                specific_children_size += child._size.height
                max_cross = max(max_cross, child._size.width)

        specific_children_size += state.gap * (len(self.children) - 1)

        if state.direction == FlexDirection.Row:
            rest = constraints.max_width - specific_children_size
        else:
            rest = constraints.max_height - specific_children_size

        main_size = specific_children_size

        for child in self.children:
            if not self.is_flex_child(child):  # type: ignore
                continue

            c = copy.copy(constraints)

            if state.direction == FlexDirection.Row:
                c.max_width = rest * child.state.flex / flex_total  # type: ignore
                child._size = child.layout(ctx, c)
                main_size = constraints.max_width
            else:
                c.max_height = rest * child.state.flex / flex_total  # type: ignore
                child._size = child.layout(ctx, c)
                main_size = constraints.max_height

        if state.direction == FlexDirection.Row:
            return orig_c.fit_size(Size(width=main_size, height=max_cross))
        else:
            return orig_c.fit_size(Size(width=max_cross, height=main_size))


class ExpandState:
    def __init__(self, *, flex: int):
        self.flex = flex

    def copy(self):
        return copy.deepcopy(self)


class Expanded(Entity):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        flex: int = 1,
        components: list[Component] = [],
        child: Entity | None = None,
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.child = child
        self.state = ExpandState(flex=flex)

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        if self.child is not None:
            self.child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        if self.child is not None:
            self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)

        for component in self.components:
            component.before_paint(self, ctx, pos, self._size, None)

        if self.child is not None:
            self.child.paint(ctx, pos)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        if self.child is not None:
            self.child._size = self.child.layout(ctx, constraints)

        return constraints.to_max_size()


class Viewport3d(Entity):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        camera: Camera,
        components: list[Component] = [],
        children: list[Entity3d] = [],
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.camera = camera
        self.children = children
        self._size = Size(width=0, height=0)

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        for child in self.children:
            child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)

        for child in self.children:
            child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)

        for component in self.components:
            component.before_paint(self, ctx, pos, self._size, None)

        pos3d = Position3d(x=pos.x, y=pos.y, z=0)

        self.camera.size = (self._size.width, self._size.height)
        for child in self.children:
            child.paint(ctx, self.camera, pos3d, Quaternion.identity())

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        return constraints.to_max_size()


class WidthState:
    def __init__(self, *, width: float):
        self.width = width

    def copy(self):
        return copy.deepcopy(self)


class WidthBox(Entity):
    state: WidthState

    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position = Position(x=0, y=0),
        width: float,
        components: list[Component] = [],
        child: Entity,
    ):
        super().__init__(tag=tag, position=position, components=components)
        self.child = child
        self.state = WidthState(width=width)
        self._state = self.state.copy()

    def create(self, canvas: Canvas):
        self.canvas = canvas

        for component in self.components:
            component.create(self)

        self.child.create(canvas)

    def destroy(self):
        for component in self.components:
            component.destroy(self)
        self.child.destroy()

    def paint(self, ctx: FrameContext, position: Position):
        pos = self.position.add(position)

        for component in self.components:
            component.before_paint(self, ctx, pos, self._size, self._state)

        child_position = Position(x=pos.x, y=pos.y)
        self.child.paint(ctx, child_position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)
        self._state = state

        c = constraints.copy()
        c.min_width = state.width
        c.max_width = state.width

        child_size = self.child.layout(ctx, c)
        self.child._size = child_size

        return constraints.fit_size(Size(width=state.width, height=child_size.height))
