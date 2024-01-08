from __future__ import annotations
import copy
from dataclasses import dataclass
import colorsys

from engine.assets import AssetManager
from engine.traits import Transitionable


class FrameContext:
    def __init__(
        self,
        *,
        delta_time: float,
        width: float,
        height: float,
        asset_manager: AssetManager,
    ):
        self.delta_time = delta_time
        self.width = width
        self.height = height
        self.asset_manager = asset_manager

    def __repr__(self):
        return f"FrameContext(delta_time={self.delta_time})"

    def __eq__(self, other):
        return self.delta_time == other.delta_time


class Size(Transitionable):
    @staticmethod
    def square(value: float) -> Size:
        return Size(width=value, height=value)

    def __init__(self, *, width: float, height: float):
        self.width = width
        self.height = height

    def copy(self):
        return copy.deepcopy(self)

    def max(self, other: Size):
        return Size(
            width=max(self.width, other.width), height=max(self.height, other.height)
        )

    def distance(self, other: Size):
        dw = self.width - other.width
        dh = self.height - other.height
        return max(abs(dw), abs(dh))

    def interpolate(self, other: Size, progress: float):
        return Size(
            width=self.width + (other.width - self.width) * progress,
            height=self.height + (other.height - self.height) * progress,
        )

    def __eq__(self, other: object):
        if not isinstance(other, Size):
            return False
        return self.width == other.width and self.height == other.height

    def __repr__(self):
        return f"Size(width={self.width}, height={self.height})"


class Position(Transitionable):
    @staticmethod
    def zero() -> Position:
        return Position(x=0, y=0)

    def __init__(self, *, x: float, y: float):
        self.x = x
        self.y = y

    def copy(self):
        return copy.copy(self)

    def add(self, other: Position):
        return Position(x=self.x + other.x, y=self.y + other.y)

    def mut_add(self, other: Position | tuple[float, float]):
        if isinstance(other, Position):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other[0]
            self.y += other[1]

    def sub(self, other: Position):
        return Position(x=self.x - other.x, y=self.y - other.y)

    def distance(self, other: Position):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def interpolate(self, other: Position, progress: float):
        return Position(
            x=self.x + (other.x - self.x) * progress,
            y=self.y + (other.y - self.y) * progress,
        )

    def __eq__(self, other: object):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Position(x={self.x}, y={self.y})"


class Constraints:
    def __init__(
        self,
        *,
        min_width: float,
        min_height: float,
        max_width: float,
        max_height: float,
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

    def copy(self):
        return copy.copy(self)

    def fit_width(self, width: float | None):
        if width is None:
            return self.max_width

        return min(self.max_width, max(self.min_width, width))

    def fit_height(self, height: float | None):
        if height is None:
            return self.max_height

        return min(self.max_height, max(self.min_height, height))

    def to_max_size(self) -> Size:
        return Size(width=self.max_width, height=self.max_height)

    def to_min_size(self) -> Size:
        return Size(width=self.min_width, height=self.min_height)

    def fit_size(self, size: Size | None) -> Size:
        if size is None:
            return Size(width=self.min_width, height=self.min_height)
        return Size(
            width=self.fit_width(size.width), height=self.fit_height(size.height)
        )

    def with_min(self, min_width: float, min_height: float):
        return Constraints(
            min_width=min_width,
            min_height=min_height,
            max_width=self.max_width,
            max_height=self.max_height,
        )

    def force_max(self):
        return Constraints(
            min_width=self.max_width,
            min_height=self.max_height,
            max_width=self.max_width,
            max_height=self.max_height,
        )

    def limit(self, size: Size | None) -> Constraints:
        if size is None:
            return self

        return Constraints(
            min_width=self.min_width,
            min_height=self.min_height,
            max_width=size.width,
            max_height=size.height,
        )

    def __repr__(self):
        return f"Constraints(min_width={self.min_width}, min_height={self.min_height}, max_width={self.max_width}, max_height={self.max_height})"


@dataclass
class Color(Transitionable):
    r: int
    g: int
    b: int

    def copy(self):
        return copy.copy(self)

    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_hls(self) -> tuple[float, float, float]:
        return colorsys.rgb_to_hls(self.r / 255.0, self.g / 255.0, self.b / 255.0)

    def to_yiq(self) -> tuple[float, float, float]:
        return colorsys.rgb_to_yiq(self.r / 255.0, self.g / 255.0, self.b / 255.0)

    def interpolate(self, other: Color, progress: float) -> Color:
        y, i, q = self.to_yiq()
        oy, oi, oq = other.to_yiq()
        return Color.from_yiq(
            y + (oy - y) * progress, i + (oi - i) * progress, q + (oq - q) * progress
        )

    def distance(self, other: Color) -> float:
        y, i, q = self.to_yiq()
        oy, oi, oq = other.to_yiq()
        return ((y - oy) ** 2 + (i - oi) ** 2 + (q - oq) ** 2) ** 0.5

    @staticmethod
    def from_hex(hex: str) -> Color:
        return Color(r=int(hex[1:3], 16), g=int(hex[3:5], 16), b=int(hex[5:7], 16))

    @staticmethod
    def from_hls(h: float, l: float, s: float) -> Color:
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return Color(r=round(r * 255), g=round(g * 255), b=round(b * 255))

    @staticmethod
    def from_yiq(y: float, i: float, q: float) -> Color:
        r, g, b = colorsys.yiq_to_rgb(y, i, q)
        return Color(r=round(r * 255), g=round(g * 255), b=round(b * 255))

    @staticmethod
    def red() -> Color:
        return Color(r=255, g=0, b=0)

    @staticmethod
    def green() -> Color:
        return Color(r=0, g=255, b=0)

    @staticmethod
    def blue() -> Color:
        return Color(r=0, g=0, b=255)

    @staticmethod
    def white() -> Color:
        return Color(r=255, g=255, b=255)

    @staticmethod
    def black() -> Color:
        return Color(r=0, g=0, b=0)

    @staticmethod
    def gray() -> Color:
        return Color(r=128, g=128, b=128)

    @staticmethod
    def yellow() -> Color:
        return Color(r=255, g=255, b=0)


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

    @staticmethod
    def symmetric(horizontal: float, vertical: float):
        return EdgeInset(
            top=vertical, right=horizontal, bottom=vertical, left=horizontal
        )

    def copy(self):
        return copy.copy(self)
