import copy
from tkinter import Canvas
from enum import StrEnum

from engine.entities.components.base import Component
from engine.models import FrameContext, Size, Constraints, Position
from engine.entities.basic import Entity

class ScreenSizeLayout(Entity):
    def __init__(self, *,
                 tag: str|None = None,
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
        constraints = Constraints(min_width=ctx.width, min_height=ctx.height, max_width=ctx.width, max_height=ctx.height)

        self.child._size = self.child.layout(ctx, constraints)

        return Size(width=ctx.width, height=ctx.height)

class EdgeInset:
    def __init__(self, top: float, right: float, bottom: float, left: float):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    @staticmethod
    def all(value: float):
        return EdgeInset(top=value, right=value, bottom=value, left=value)

    @staticmethod
    def horizontal(value: float):
        return EdgeInset(top=0, right=value, bottom=0, left=value)

    @staticmethod
    def vertical(value: float):
        return EdgeInset(top=value, right=0, bottom=value, left=0)

    def copy(self):
        return copy.copy(self)

class PaddingState:
    def __init__(self, padding: EdgeInset):
        self.padding = padding

    def copy(self):
        return copy.deepcopy(self)

class Padding(Entity):
    def __init__(self, *,
                 tag: str|None = None,
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

        child_position = Position(x=pos.x + self._state.padding.left, y=pos.y + self._state.padding.top)
        self.child.paint(ctx, child_position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self,ctx, state)
        self._state = state

        c = constraints.copy()
        x_padding = state.padding.left + state.padding.right
        y_padding = state.padding.top + state.padding.bottom

        c.min_width -= x_padding
        c.max_width -= x_padding
        c.min_height -= y_padding
        c.max_height -= y_padding

        child_size = self.child.layout(ctx, c)
        self.child._size = child_size

        return Size(width=child_size.width + x_padding, height=child_size.height + y_padding)

class Center(Entity):
    def __init__(self, *,
                 tag: str|None = None,
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

        child_position = Position(x=pos.x + (self._size.width - self.child._size.width) / 2,
                                  y=pos.y + (self._size.height - self.child._size.height) / 2)

        self.child.paint(ctx, child_position)

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        self.child._size = self.child.layout(ctx, constraints.with_min(0, 0))

        return constraints.to_max_size()

class Stack(Entity):
    def __init__(self, *,
                 tag: str|None = None,
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
        constraints = constraints.copy()
        constraints.min_width = 0
        constraints.min_height = 0
        max_w = 0
        max_h = 0
        for child in self.children:
            child_size = child.layout(ctx, constraints)
            child._size = child_size
            max_w = max(max_w, child_size.width + child.position.x)
            max_h = max(max_h, child_size.height + child.position.y)

        return Size(width=max_w, height=max_h)

class FlexDirection(StrEnum):
    Row = 'Row'
    Column = 'Column'

    def __repr__(self):
        if self == FlexDirection.Row:
            return 'Row'
        elif self == FlexDirection.Column:
            return 'Column'

class FlexState:
    def __init__(self, *, direction: FlexDirection):
        self.direction = direction

    def copy(self):
        return FlexState(direction=self.direction)

class Flex(Entity):
    def __init__(self, *,
                 tag:str|None=None,
                 position: Position = Position(x=0, y=0), 
                 direction: FlexDirection, 
                 components: list[Component] = [],
                 children: list[Entity] = []
                 ):
        super().__init__(tag=tag, position=position, components=components)
        self.children = children
        self.state = FlexState(direction=direction)
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
            child.paint(ctx, pos)
            if self._state.direction == FlexDirection.Row:
                pos.x += child._size.width
            else:
                pos.y += child._size.height

    def is_flex_child(self, child: Entity) -> bool:
        return hasattr(child, 'state') and hasattr(child.state, 'flex') and child.state.flex != 0 # type: ignore

    def layout(self, ctx: FrameContext, constraints: Constraints) -> Size:
        state = self.state.copy()
        for component in self.components:
            component.before_layout(self, ctx, state)

        specific_children_size = 0
        flex_total = 0
        max_cross = 0

        constraints.min_width = 0
        constraints.min_height = 0

        for child in self.children:
            if self.is_flex_child(child):
                flex_total += child.state.flex # type: ignore
                continue

            if state.direction == FlexDirection.Row:
                child._size = child.layout(ctx, constraints)
                specific_children_size += child._size.width
                max_cross = max(max_cross, child._size.height)
            else:
                child._size = child.layout(ctx, constraints)
                specific_children_size += child._size.height
                max_cross = max(max_cross, child._size.width)

        if state.direction == FlexDirection.Row:
            rest = constraints.max_width - specific_children_size
        else:
            rest = constraints.max_height - specific_children_size

        for child in self.children:
            if not self.is_flex_child(child): # type: ignore
                continue

            c = copy.copy(constraints)

            if state.direction == FlexDirection.Row:
                c.max_width = rest * child.state.flex / flex_total # type: ignore
                child._size = child.layout(ctx, c)
            else:
                c.max_height = rest * child.state.flex / flex_total # type: ignore
                child._size = child.layout(ctx, c)

        if state.direction == FlexDirection.Row:
            return Size(width=constraints.max_width, height=max_cross)
        else:
            return Size(width=max_cross, height=constraints.max_height)

class ExpandState:
    def __init__(self, *, flex: int):
        self.flex = flex

    def copy(self):
        return copy.deepcopy(self)

class Expanded(Entity):
    def __init__(self, *,
                 tag:str|None=None,
                 position: Position = Position(x=0, y=0), 
                 flex: int = 1,
                 components: list[Component] = [],
                 child: Entity|None = None
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

