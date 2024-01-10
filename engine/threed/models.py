from __future__ import annotations
import copy
import math
from dataclasses import astuple, dataclass

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

    def mul(self, other: Position3d | float):
        if type(other) == float or type(other) == int:
            return Position3d(x=self.x * other, y=self.y * other, z=self.z * other)
        else:
            return Position3d(
                x=self.x * other.x, y=self.y * other.y, z=self.z * other.z
            )

    def normalized(self):
        length = self.length()
        if length == 0:
            return Position3d(x=0, y=0, z=0)
        return Position3d(x=self.x / length, y=self.y / length, z=self.z / length)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

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
        return copy.copy(self)

    def dot(self, other: Position3d):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def angle(self, other: Position3d):
        return math.acos(self.dot(other) / (self.length() * other.length()))

    def cross(self, other: Position3d):
        return Position3d(
            x=self.y * other.z - self.z * other.y,
            y=self.z * other.x - self.x * other.z,
            z=self.x * other.y - self.y * other.x,
        )

    def max_by_length(self, other: Position3d):
        if self.length() > other.length():
            return self
        else:
            return other

    def __eq__(self, other: Position3d):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self):
        return f"Position3d({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


@dataclass
class Size3d:
    width: float
    height: float
    depth: float


@dataclass
class Quaternion(Transitionable):
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
        ).normalized()

    @staticmethod
    def identity():
        return Quaternion(w=1, i=0, j=0, k=0)

    def copy(self):
        return copy.copy(self)

    def __eq__(self, other: Quaternion):
        return (
            self.w == other.w
            and self.i == other.i
            and self.j == other.j
            and self.k == other.k
        )

    def distance(self, other: Quaternion) -> float:
        """
        Angle between two quaternions
        """

        dot_product = self.normalized().dot(other.normalized())

        if dot_product < 0:
            dot_product = -dot_product

        dot_product = min(1, max(-1, dot_product))

        return math.acos(dot_product)

    def magnitude(self) -> float:
        return math.sqrt(self.w**2 + self.i**2 + self.j**2 + self.k**2)

    def normalized(self) -> Quaternion:
        magnitude = self.magnitude()
        return Quaternion(
            w=self.w / magnitude,
            i=self.i / magnitude,
            j=self.j / magnitude,
            k=self.k / magnitude,
        )

    def negate(self) -> Quaternion:
        return Quaternion(w=-self.w, i=-self.i, j=-self.j, k=-self.k)

    def dot(self, other: Quaternion) -> float:
        return self.w * other.w + self.i * other.i + self.j * other.j + self.k * other.k

    def interpolate(self, other: Quaternion, progress: float) -> Quaternion:
        a = self.normalized()
        b = other.normalized()

        theta = a.distance(b)

        t1 = math.sin((1 - progress) * theta) / math.sin(theta)
        t2 = math.sin(progress * theta) / math.sin(theta)

        result = Quaternion(
            w=a.w * t1 + b.w * t2,
            i=a.i * t1 + b.i * t2,
            j=a.j * t1 + b.j * t2,
            k=a.k * t1 + b.k * t2,
        )

        return result.normalized()


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
        screen_x = x * focal_z / (z + focal_z)
        screen_y = y * focal_z / (z + focal_z) * aspect_ratio

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

    def screen_to_world(self, x: float, y: float, plane_z: float):
        aspect_ratio = self.size[0] / self.size[1]
        focal_z = 1 / math.tan(math.radians(self.fov / 2))
        near_plane_x = x / self.size[0] * 2 - 1
        near_plane_y = y / self.size[1] * 2 - 1

        plane_z = plane_z - self.position.z

        target_x = near_plane_x * (plane_z + focal_z) / focal_z
        target_y = near_plane_y * (plane_z + focal_z) / focal_z / aspect_ratio

        return Position3d(
            x=target_x,
            y=target_y,
            z=plane_z,
        )
