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

    def __repr__(self):
        return f"Size(width={self.width}, height={self.height})"

class DefinedSize():
    def __init__(self, *, width: float, height: float):
        self.width = width
        self.height = height

    def copy(self):
        return copy.copy(self)

    def __repr__(self):
        return f"DefinedSize(width={self.width}, height={self.height})"

class Position:
    def __init__(self, *, x: float, y: float):
        self.x = x
        self.y = y

    def copy(self):
        return copy.copy(self)

    def add(self, other):
        return Position(x=self.x + other.x, y=self.y + other.y)

    def __repr__(self):
        return f"Position(x={self.x}, y={self.y})"
        
class Constraints:
    def __init__(self, *,
                 min_width: float,
                 min_height: float,
                 max_width: float|None = None,
                 max_height: float|None = None
                 ):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

    @staticmethod
    def unbounded():
        return Constraints(min_width=0, min_height=0, max_width=None, max_height=None)

    def copy(self):
        return copy.copy(self)

    def fit_width(self, width: float|None):
        if width is None:
            if self.max_width is None:
                raise ValueError("Cannot fit None width into unbounded constraints")
            return self.max_width

        minimum = max(self.min_width, width)

        if self.max_width is None:
            return minimum

        return min(self.max_width, minimum)

    def fit_height(self, height: float|None):
        if height is None:
            if self.max_height is None:
                raise ValueError("Cannot fit None height into unbounded constraints")
            return self.max_height

        minimum = max(self.min_height, height)

        if self.max_height is None:
            return minimum

        return min(self.max_height, minimum)

    def to_max_defined_size(self) -> DefinedSize:
        if self.max_width is None or self.max_height is None:
            raise ValueError("Cannot convert unbounded constraints to DefinedSize")

        return DefinedSize(width=self.max_width, height=self.max_height)

    def fit_size(self, size: Size) -> DefinedSize:
        return DefinedSize(width=self.fit_width(size.width), height=self.fit_height(size.height))

    def is_unbounded(self):
        return self.max_width is None or self.max_height is None

    def __repr__(self):
        return f"Constraints(min_width={self.min_width}, min_height={self.min_height}, max_width={self.max_width}, max_height={self.max_height})"

