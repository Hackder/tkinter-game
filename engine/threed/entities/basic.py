import math
import copy
from abc import ABC, abstractmethod
from tkinter import Canvas
from engine.threed.models import Position3d, Quaternion, Camera, Size3d
from engine.models import FrameContext
from engine.threed.entities.components.base import Component3d
from typing import Any, Callable


class Entity3d(ABC):
    state: Any
    canvas: Canvas

    @abstractmethod
    def __init__(self, *, tag: str | None, components: list[Component3d] = []):
        self.tag = tag
        self.components = components

    @abstractmethod
    def create(self, canvas: Canvas):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def paint(
        self,
        ctx: FrameContext,
        camera: Camera,
        position: Position3d,
        rotation: Quaternion,
    ):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(tag={self.tag})"


class CubeState:
    def __init__(self, position: Position3d, rotation: Quaternion, size: Size3d):
        self.position = position
        self.rotation = rotation
        self.size = size

    def copy(self):
        return copy.deepcopy(self)


TransformFn = Callable[[float, float], tuple[float, float]]

class BaseCube(Entity3d):
    state: CubeState

    def __init__(
        self,
        *,
        tag: str | None,
        position: Position3d,
        rotation: Quaternion,
        components: list[Component3d] = [],
        size: Size3d = Size3d(0, 0, 0),
    ):
        super().__init__(tag=tag, components=components)
        self.state = CubeState(position, rotation, size)

    @abstractmethod
    def create(self, canvas: Canvas):
        pass

    @abstractmethod
    def destroy(self):
        pass

    def paint(
        self,
        ctx: FrameContext,
        camera: Camera,
        position: Position3d,
        rotation: Quaternion,
    ):
        state = self.state.copy()
        for component in self.components:
            component.before_paint(self, ctx, position, rotation, state.size, state)

        final_position = position.add(state.position.rotated(rotation))

        positions: list[tuple[Position3d, str]] = [
                (Position3d(0, 0, -state.size.depth / 2), 'front'),
                (Position3d(0, 0, state.size.depth / 2), 'back'),
                (Position3d(-state.size.width / 2, 0, 0), 'left'),
                (Position3d(state.size.width / 2, 0, 0), 'right'),
                (Position3d(0, state.size.height / 2, 0), 'top'),
                (Position3d(0, -state.size.height / 2, 0), 'bottom'),
                ]

        def is_visible(pos: Position3d):
            face_center = final_position.add(pos.rotated(state.rotation))
            face_normal = face_center.sub(final_position).normalized()
            # face_normal = final_position.sub(face_center).normalized()
            camera_vec = final_position.sub(camera.focal_position()).normalized()
            return face_normal.dot(camera_vec) < -0.01

        visible_sides = [p[1] for p in positions if is_visible(p[0])]

        self.front(
            ctx,
            state.size.width,
            state.size.height,
            lambda x, y: camera.project(
                final_position.add(
                    Position3d(x, y, -state.size.depth / 2).rotated(
                        state.rotation
                    )
                )
            ),
            'front' in visible_sides
        )

        self.back(
            ctx,
            state.size.width,
            state.size.height,
            lambda x, y: camera.project(
                final_position.add(
                    Position3d(x, y, state.size.depth / 2).rotated(
                        state.rotation
                    )
                )
            ),
            'back' in visible_sides
        )

        self.left(
            ctx,
            state.size.depth,
            state.size.height,
            lambda x, y: camera.project(
                final_position.add(
                    Position3d(-state.size.width / 2, y, x).rotated(
                        state.rotation
                    )
                )
            ),
            'left' in visible_sides
        )

        self.right(
            ctx,
            state.size.depth,
            state.size.height,
            lambda x, y: camera.project(
                final_position.add(
                    Position3d(state.size.width / 2, y, x).rotated(
                        state.rotation
                    )
                )
            ),
            'right' in visible_sides
        )

        self.top(
            ctx,
            state.size.width,
            state.size.depth,
            lambda x, y: camera.project(
                final_position.add(
                    Position3d(x, state.size.height / 2, y).rotated(
                        state.rotation
                    )
                )
            ),
            'top' in visible_sides
        )

        self.bottom(
            ctx,
            state.size.width,
            state.size.depth,
            lambda x, y: camera.project(
                final_position.add(
                    Position3d(x, -state.size.height / 2, y).rotated(
                        state.rotation
                    )
                )
            ),
            'bottom' in visible_sides
        )

    @abstractmethod
    def front(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        pass

    @abstractmethod
    def back(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        pass

    @abstractmethod
    def left(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        pass

    @abstractmethod
    def right(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        pass

    @abstractmethod
    def top(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        pass

    @abstractmethod
    def bottom(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        pass


class Dice(BaseCube):
    def __init__(
        self,
        *,
        tag: str | None = None,
        position: Position3d,
        rotation: Quaternion = Quaternion.identity(),
        size: Size3d,
        components: list[Component3d] = [],
    ):
        super().__init__(tag=tag, position=position, rotation=rotation, size=size, components=components)
        self.current_idx = 0
        self.last_raise_idx = 0
        self.ids = []


    def create(self, canvas: Canvas):
        self.canvas = canvas
        for _ in range(27):
            self.ids.append(canvas.create_polygon(
                0, 0, 0, 0, 0, 0, 0, 0, fill="white", outline="black"
            ))

        for component in self.components:
            component.create(self)

    def destroy(self):
        for component in self.components:
            component.destroy(self)

        for id in self.ids:
            self.canvas.delete(id)

    def paint(self, ctx: FrameContext, camera: Camera, position: Position3d, rotation: Quaternion):
        self.current_idx = 0
        self.last_raise_idx = 0
        return super().paint(ctx, camera, position, rotation)

    def side_vertices(self, w: float, h: float, transform: TransformFn):
        return [
            *transform(-w / 2, -h / 2),
            *transform(w / 2, -h / 2),
            *transform(w / 2, h / 2),
            *transform(-w / 2, h / 2),
        ]


    def point(self, w, h, x, y, transform):
        small_size = w / 6

        xx = x * w - small_size / 2
        yy = y * h - small_size / 2

        return [
            *transform(xx, yy),
            *transform(xx + small_size, yy),
            *transform(xx + small_size, yy + small_size),
            *transform(xx, yy + small_size),
                ]

    def next_id(self):
        self.current_idx += 1
        return self.ids[self.current_idx - 1]

    def raise_last(self):
        for idx in range(self.last_raise_idx, self.current_idx):
            self.canvas.tag_raise(self.ids[idx])
        self.last_raise_idx = self.current_idx

    def front(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        id = self.next_id()
        self.canvas.coords(id, *self.side_vertices(w, h, transform))
        id = self.next_id()
        self.canvas.coords(id, *self.point(w, h, 0, 0, transform))
        self.canvas.itemconfig(id, fill="black")

        # self.state.rotation = Quaternion.from_axis_angle(Position3d(1, 0, 0), math.pi/8)
        self.state.rotation *= Quaternion.from_axis_angle(Position3d(1, 0, 0), math.pi/4 * ctx.delta_time)
        # self.state.rotation *= Quaternion.from_axis_angle(Position3d(0, 1, 1), math.pi/3 * ctx.delta_time)

        if visible:
            self.raise_last()
        else:
            self.last_raise_idx = self.current_idx


    def back(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        self.canvas.coords(self.next_id(), *self.side_vertices(w, h, transform))
        for x in [-1, 1]:
            for i in range(3):
                id = self.next_id()
                self.canvas.coords(id, *self.point(w, h, x * 0.2, -0.3 + 0.3*i, transform))
                self.canvas.itemconfig(id, fill="black")


        if visible:
            self.raise_last()
        else:
            self.last_raise_idx = self.current_idx

    def left(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        id = self.next_id()
        self.canvas.coords(id, *self.side_vertices(w, h, transform))

        for y in [-1, 1]:
            id = self.next_id()
            self.canvas.coords(id, *self.point(w, h, 0,  y * 0.2, transform))
            self.canvas.itemconfig(id, fill="black")


        if visible:
            self.raise_last()
        else:
            self.last_raise_idx = self.current_idx

    def right(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        id = self.next_id()
        self.canvas.coords(id, *self.side_vertices(w, h, transform))

        for y in [-1, 1]:
            for x in [-1, 1]:
                id = self.next_id()
                self.canvas.coords(id, *self.point(w, h, x * 0.22,  y * 0.22, transform))
                self.canvas.itemconfig(id, fill="black")

        id = self.next_id()
        self.canvas.coords(id, *self.point(w, h, 0, 0, transform))
        self.canvas.itemconfig(id, fill="black")

        if visible:
            self.raise_last()
        else:
            self.last_raise_idx = self.current_idx

    def top(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        id = self.next_id()
        self.canvas.coords(id, *self.side_vertices(w, h, transform))

        for x in [-1, 0, 1]:
            id = self.next_id()
            self.canvas.coords(id, *self.point(w, h, x * 0.3, 0, transform))
            self.canvas.itemconfig(id, fill="black")

        if visible:
            self.raise_last()
        else:
            self.last_raise_idx = self.current_idx

    def bottom(self, ctx: FrameContext, w: float, h: float, transform: TransformFn, visible: bool):
        id = self.next_id()
        self.canvas.coords(id, *self.side_vertices(w, h, transform))

        for y in [-1, 1]:
            for x in [-1, 1]:
                id = self.next_id()
                self.canvas.coords(id, *self.point(w, h, x * 0.20,  y * 0.20, transform))
                self.canvas.itemconfig(id, fill="black")

        if visible:
            self.raise_last()
        else:
            self.last_raise_idx = self.current_idx


