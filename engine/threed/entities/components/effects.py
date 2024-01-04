from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from engine.models import FrameContext, Transitionable
from engine.entities.components.effects import Easing
from engine.threed.entities.basic import Entity3d
from engine.threed.entities.components.base import Component3d
from engine.threed.models import Position3d, Quaternion, Size3d


class Object3dTransition(Component3d, ABC):
    def __init__(
        self,
        *,
        speed: float | None = None,
        duration: float | None = 1,
        skip: float | None = None,
        easing=Easing.linear,
    ):
        self.type = type
        self.speed = speed
        self.duration = duration
        self.skip = skip
        self.last_value = None
        self.target_value = None
        self.value = None
        self.progress = 0
        self.distance = 0
        self.easing = easing

    @abstractmethod
    def selector(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
    ) -> Transitionable:
        pass

    @abstractmethod
    def setter(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
        value: Transitionable,
    ):
        pass

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
        new_value = self.selector(entity, ctx, position, rotation, size, state)

        if self.last_value is None or self.value is None or self.target_value is None:
            self.last_value = new_value
            self.target_value = new_value
            self.value = new_value
            return

        if new_value != self.target_value:
            self.last_value = self.value
            self.target_value = new_value.copy()
            self.distance = new_value.distance(self.last_value)
            self.progress = 0
            if self.skip is not None and self.distance > self.skip:
                self.progress = 1

        if self.progress == 1 or self.distance == 0:
            return

        if self.speed is not None:
            self.progress += self.speed / self.distance * ctx.delta_time
        elif self.duration is not None:
            self.progress += ctx.delta_time / self.duration
        else:
            raise Exception("Either speed or duration must be set")

        self.progress = min(self.progress, 1)

        self.value = self.last_value.interpolate(
            self.target_value, self.easing(self.progress)
        )

        self.setter(entity, ctx, position, rotation, size, state, self.value)


class Position3dTransition(Object3dTransition):
    def selector(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
    ) -> Position3d:
        if state is None or not hasattr(state, "position"):
            raise Exception("State must have a position property")

        return state.position

    def setter(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
        value: Position3d,
    ):
        if state is None or not hasattr(state, "position"):
            raise Exception("State must have a position property")

        state.position = value


class Rotation3dTransition(Object3dTransition):
    def selector(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
    ) -> Quaternion:
        if state is None or not hasattr(state, "rotation"):
            raise Exception("State must have a rotation property")

        return state.rotation

    def setter(
        self,
        entity: Entity3d,
        ctx: FrameContext,
        position: Position3d,
        rotation: Quaternion,
        size: Size3d,
        state: Any | None,
        value: Quaternion,
    ):
        if state is None or not hasattr(state, "rotation"):
            raise Exception("State must have a rotation property")

        state.rotation = value


class SetCursor(Component3d):
    def __init__(self, *, tag: str = "", cursor="hand2"):
        self.cursor = cursor
        self.tag = tag
        self.event_ids = []

    def create(self, entity):
        self.entity = entity
        if self.tag:
            id = self.entity.canvas.tag_bind(self.tag, "<Enter>", self.enter, add="+")
            id2 = self.entity.canvas.tag_bind(self.tag, "<Leave>", self.enter, add="+")
            self.event_ids.append(id)
            self.event_ids.append(id2)
        else:
            for id in entity.ids:
                event_id = self.entity.canvas.tag_bind(
                    id, "<Enter>", self.enter, add="+"
                )
                event_id2 = self.entity.canvas.tag_bind(
                    id, "<Leave>", self.leave, add="+"
                )
                self.event_ids.append(event_id)
                self.event_ids.append(event_id2)

    def destroy(self, entity: Entity3d):
        if self.tag:
            for id in self.event_ids:
                self.entity.canvas.tag_unbind(self.tag, "<Enter>", id)
                self.entity.canvas.tag_unbind(self.tag, "<Leave>", id)
        else:
            for i, id in enumerate(self.entity.ids):
                self.entity.canvas.tag_unbind(id, "<Enter>", self.event_ids[i * 2])
                self.entity.canvas.tag_unbind(id, "<Leave>", self.event_ids[i * 2 + 1])

        self.event_ids = []

    def enter(self, e):
        self.entity.canvas.config(cursor=self.cursor)

    def leave(self, e):
        self.entity.canvas.config(cursor="")
