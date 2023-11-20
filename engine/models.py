from __future__ import annotations
import copy

class FrameContext:
    def __init__(self, *, delta_time: float, width: float, height: float):
        self.delta_time = delta_time
        self.width = width
        self.height = height

    def __repr__(self):
        return f"FrameContext(delta_time={self.delta_time})"

    def __eq__(self, other):
        return self.delta_time == other.delta_time

class Size:
    def __init__(self, *, width: float|None, height: float|None):
        self.width = width
        self.height = height

    @staticmethod
    def unbounded():
        return Size(width=None, height=None)

    def copy(self):
        return copy.copy(self)

    def max(self, other: Size):
        return Size(
                width=max(self.width, other.width) if self.width is not None and other.width is not None else None,
                height=max(self.height, other.height) if self.height is not None and other.height is not None else None
                )
    

    def __repr__(self):
        return f"Size(width={self.width}, height={self.height})"

class DefinedSize(Size):
    def __init__(self, *, width: float, height: float):
        self.width = width
        self.height = height

    def copy(self):
        return copy.deepcopy(self)

    def max(self, other: DefinedSize):
        return DefinedSize(width=max(self.width, other.width), height=max(self.height, other.height))

    def distance(self, other: DefinedSize):
        dw = self.width - other.width
        dh = self.height - other.height
        return max(abs(dw), abs(dh))

    def lerp(self, other: DefinedSize, progress: float):
        return DefinedSize(width=self.width + (other.width - self.width) * progress, height=self.height + (other.height - self.height) * progress)

    def __eq__(self, other: DefinedSize):
        return self.width == other.width and self.height == other.height

    def __repr__(self):
        return f"DefinedSize(width={self.width}, height={self.height})"

class Position:
    def __init__(self, *, x: float, y: float):
        self.x = x
        self.y = y

    def copy(self):
        return copy.copy(self)

    def add(self, other: Position):
        return Position(x=self.x + other.x, y=self.y + other.y)

    def sub(self, other: Position):
        return Position(x=self.x - other.x, y=self.y - other.y)

    def distance(self, other: Position):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def lerp(self, other: Position, progress: float):
        return Position(x=self.x + (other.x - self.x) * progress, y=self.y + (other.y - self.y) * progress)

    def __eq__(self, other: Position):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Position(x={self.x}, y={self.y})"
        
class Constraints:
    def __init__(self, *,
                 min_width: float,
                 min_height: float,
                 max_width: float,
                 max_height: float
                 ):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

    def copy(self):
        return copy.copy(self)

    def fit_width(self, width: float|None):
        if width is None:
            return self.max_width

        return min(self.max_width, max(self.min_width, width))

    def fit_height(self, height: float|None):
        if height is None:
            return self.max_height

        return min(self.max_height, max(self.min_height, height))

    def to_max_defined_size(self) -> DefinedSize:
        return DefinedSize(width=self.max_width, height=self.max_height)

    def fit_size(self, size: Size) -> DefinedSize:
        return DefinedSize(width=self.fit_width(size.width), height=self.fit_height(size.height))

    def with_min(self, min_width: float, min_height: float):
        return Constraints(min_width=min_width, min_height=min_height, max_width=self.max_width, max_height=self.max_height)

    def limit(self, size: Size) -> Constraints:
        max_w = size.width if size.width is not None else self.max_width
        max_h = size.height if size.height is not None else self.max_height
        return Constraints(min_width=self.min_width, min_height=self.min_height, max_width=max_w, max_height=max_h)

    def __repr__(self):
        return f"Constraints(min_width={self.min_width}, min_height={self.min_height}, max_width={self.max_width}, max_height={self.max_height})"

