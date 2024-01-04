import math
from typing import Any
from timeit import default_timer as timer

from engine.threed.entities.components.effects import SetCursor
from engine.threed.entities.components.base import Component3d
from engine.entities.layout import ScreenSizeLayout, Viewport3d
from engine.threed.entities.basic import Dice, Entity3d
from engine.threed.models import Position3d, Size3d, Camera, Quaternion
from engine.models import FrameContext

natural_directions = [
    Position3d(1, 0, 0),
    Position3d(-1, 0, 0),
    Position3d(0, 1, 0),
    Position3d(0, -1, 0),
    Position3d(0, 0, 1),
    Position3d(0, 0, -1),
]


class Throwable(Component3d):
    def __init__(self, initial_speed=Position3d(x=0, y=0, z=0)):
        self.dragging = False
        self.drag_start = Position3d(x=0, y=0, z=0)
        self.camera = None
        self.speed = initial_speed
        self.last_move = timer()

    def create(self, entity):
        self.entity = entity
        entity.canvas.bind("<B1-Motion>", self.drag)
        for id in entity.ids:
            entity.canvas.tag_bind(id, "<Button-1>", self.click, add="+")
            entity.canvas.tag_bind(id, "<ButtonRelease-1>", self.release, add="+")

    def before_paint(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        camera: Camera,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
    ):
        self.camera = camera
        assert state is not None

        l_screen_pos = camera.project(
            entity.state.position.sub(Position3d(entity.state.size.width / 2, 0, 0))
        )
        r_screen_pos = camera.project(
            entity.state.position.add(Position3d(entity.state.size.width / 2, 0, 0))
        )
        t_screen_pos = camera.project(
            entity.state.position.sub(Position3d(0, entity.state.size.height / 2, 0))
        )
        b_screen_pos = camera.project(
            entity.state.position.add(Position3d(0, entity.state.size.height / 2, 0))
        )

        top_left = camera.screen_to_world(0, 0, entity.state.position.z)
        bottom_right = camera.screen_to_world(
            camera.size[0], camera.size[1], entity.state.position.z
        )

        if l_screen_pos[0] < 0:
            self.speed.x *= -1
            entity.state.position.x = top_left.x + entity.state.size.width / 2
        if r_screen_pos[0] > camera.size[0]:
            self.speed.x *= -1
            entity.state.position.x = bottom_right.x - entity.state.size.width / 2
        if t_screen_pos[1] < 0:
            self.speed.y *= -1
            entity.state.position.y = top_left.y + entity.state.size.height / 2
        if b_screen_pos[1] > camera.size[1]:
            self.speed.y *= -1
            entity.state.position.y = bottom_right.y - entity.state.size.height / 2

        if not self.dragging:
            perpendicular_axis = self.speed.cross(Position3d(0, 0, 1)).normalized()
            angle = self.speed.length() / (size.width * 4) * math.pi * ctx.delta_time
            angular_speed = Quaternion.from_axis_angle(perpendicular_axis, angle)

            entity.state.rotation = angular_speed * entity.state.rotation

            closest_direction = None
            reference_direction = None
            perpendicular_axis = self.speed.cross(Position3d(0, 0, 1)).normalized()
            for reference_base in [Position3d(0, 0, 1), Position3d(0, 1, 0)]:
                closest_direction = None
                closest_distance = 0
                reference = reference_base.rotated(entity.state.rotation)
                for direction in natural_directions:
                    distance = direction.dot(reference)
                    if distance > closest_distance:
                        closest_direction = direction
                        closest_distance = distance

                assert closest_direction is not None

                if closest_direction.z != 0:
                    reference_direction = reference
                    break
            else:
                reference_direction = Position3d(1, 0, 0).rotated(entity.state.rotation)
                if reference_direction.dot(Position3d(0, 0, 1)) < 0:
                    closest_direction = Position3d(0, 0, -1)
                else:
                    closest_direction = Position3d(0, 0, 1)

            rotation = Quaternion.from_axis_angle(
                reference_direction.cross(closest_direction), math.pi * ctx.delta_time
            )
            entity.state.rotation = rotation * entity.state.rotation

            dir = Position3d(0, 0, 1).rotated(rotation)
            self.speed.x += dir.x * ctx.delta_time * state.size.width
            self.speed.y += dir.y * ctx.delta_time * state.size.width

            if self.speed.length() > 3:
                entity.state.position = entity.state.position.add(
                    self.speed.mul(ctx.delta_time)
                )

            deceleration = self.speed.mul(-1).max_by_length(
                self.speed.normalized().mul(-200)
            )

            self.speed.x += deceleration.x * ctx.delta_time
            self.speed.y += deceleration.y * ctx.delta_time

    def click(self, e):
        if self.camera is None:
            return

        self.dragging = True
        self.drag_start = self.camera.screen_to_world(
            e.x, e.y, self.entity.state.position.z
        )
        self.last_move = timer()

    def drag(self, e):
        if self.camera is None:
            return

        world_pos = self.camera.screen_to_world(e.x, e.y, self.entity.state.position.z)

        if self.dragging:
            now = timer()
            delta = now - self.last_move

            self.speed = Position3d(
                x=(world_pos.x - self.drag_start.x) / delta,
                y=(world_pos.y - self.drag_start.y) / delta,
                z=0,
            )
            self.entity.state.position.x += world_pos.x - self.drag_start.x
            self.entity.state.position.y += world_pos.y - self.drag_start.y
            self.drag_start = Position3d(x=world_pos.x, y=world_pos.y, z=0)
            self.last_move = now

    def release(self, e):
        self.dragging = False


class FreeCube:
    @staticmethod
    def build():
        return Viewport3d(
            camera=Camera(
                position=Position3d(x=0, y=0, z=-500),
                fov=30,
            ),
            children=[
                Dice(
                    position=Position3d(x=0, y=-60, z=0),
                    size=Size3d(width=10, height=10, depth=10),
                    rotation=Quaternion.from_axis_angle(
                        Position3d(0, 1, 1), -math.pi / 4
                    ),
                    components=[
                        SetCursor(cursor="hand1"),
                        Throwable(),
                    ],
                )
            ],
        )
