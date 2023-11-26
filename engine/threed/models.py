from __future__ import annotations
import copy
import math
from dataclasses import dataclass

from engine.traits import Transitionable

@dataclass
class Position3d(Transitionable):
    x: float
    y: float
    z: float

    def to_quaternion(self):
        return Quaternion(w=0, i=self.x, j=self.y, k=self.z)

    def rotated(self, rotation: Quaternion):
        r = rotation * self.to_quaternion() * rotation.conjugate()
        return Position3d(x=r.i, y=r.j, z=r.k)

    def add(self, other: Position3d):
        return Position3d(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def sub(self, other: Position3d):
        return Position3d(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def normalized(self):
        length = self.length()
        return Position3d(
            x=self.x / length, y=self.y / length, z=self.z / length
        )

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def distance(self, other: Position3d):
        return math.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )

    def interpolate(self, other: Position3d, progress: float) -> Position3d:
        return Position3d(
            x=self.x + (other.x - self.x) * progress,
            y=self.y + (other.y - self.y) * progress,
            z=self.z + (other.z - self.z) * progress,
        )

    def copy(self):
        return copy.deepcopy(self)

    def dot(self, other: Position3d):
        return self.x * other.x + self.y * other.y + self.z * other.z

@dataclass
class Size3d:
    width: float
    height: float
    depth: float


@dataclass
class Quaternion:
    w: float
    i: float
    j: float
    k: float

    def __mul__(self, other: Quaternion | float):
        if isinstance(other, float):
            return Quaternion(
                w=self.w * other, i=self.i * other, j=self.j * other, k=self.k * other
            )

        return Quaternion(
            w=self.w * other.w - self.i * other.i - self.j * other.j - self.k * other.k,
            i=self.w * other.i + self.i * other.w + self.j * other.k - self.k * other.j,
            j=self.w * other.j - self.i * other.k + self.j * other.w + self.k * other.i,
            k=self.w * other.k + self.i * other.j - self.j * other.i + self.k * other.w,
        )

    def conjugate(self):
        return Quaternion(w=self.w, i=-self.i, j=-self.j, k=-self.k)

    @staticmethod
    def from_axis_angle(axis: Position3d, angle: float):
        return Quaternion(
            w=math.cos(angle / 2),
            i=axis.x * math.sin(angle / 2),
            j=axis.y * math.sin(angle / 2),
            k=axis.z * math.sin(angle / 2),
        )

    @staticmethod
    def identity():
        return Quaternion(w=1, i=0, j=0, k=0)


@dataclass
class Camera:
    position: Position3d
    fov: float = 90
    size: tuple[float, float] = (0, 0)

    def project(self, position: Position3d) -> tuple[float, float]:
        x = position.x - self.position.x
        y = position.y - self.position.y
        z = position.z - self.position.z

        if z <= 0:
            return (math.inf, math.inf)

        aspect_ratio = self.size[0] / self.size[1]

        focal_z = 1 / math.tan(math.radians(self.fov / 2))
        screen_x = x * focal_z / z
        screen_y = y * focal_z / z * aspect_ratio

        return (
            (screen_x + 1) * self.size[0] / 2,
            (screen_y + 1) * self.size[1] / 2,
        )

    def focal_position(self) -> Position3d:
        return Position3d(
            x=self.position.x,
            y=self.position.y,
            z=self.position.z - 1 / math.tan(math.radians(self.fov / 2)),
        )


