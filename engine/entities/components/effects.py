from __future__ import annotations
from random import random
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from engine.models import Position, Size, FrameContext
from engine.traits import Transitionable
from engine.animation.utils import Easing
from engine.entities.basic import Entity
from engine.entities.components.base import Component


class ObjectTransition(Component, ABC):
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
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ) -> Transitionable:
        pass

    @abstractmethod
    def setter(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
        value: Transitionable,
    ):
        pass

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ):
        new_value = self.selector(entity, ctx, position, size, state)

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

        self.setter(entity, ctx, position, size, state, self.value)


class ObjectLayoutTransition(Component, ABC):
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
        self, entity: Entity, ctx: FrameContext, state: object | None
    ) -> Transitionable:
        pass

    @abstractmethod
    def setter(
        self,
        entity: Entity,
        ctx: FrameContext,
        state: object | None,
        value: Transitionable,
    ):
        pass

    def before_layout(self, entity: Entity, ctx: FrameContext, state: object | None):
        new_value = self.selector(entity, ctx, state)

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

        self.setter(entity, ctx, state, self.value)


class PositionTransition(ObjectTransition):
    def __init__(
        self,
        *,
        speed: float | None = None,
        duration: float | None = 1,
        skip: float | None = None,
        easing=Easing.linear,
    ):
        super().__init__(speed=speed, duration=duration, skip=skip, easing=easing)

    def selector(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: object | None,
    ) -> Position:
        return position

    def setter(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: object | None,
        value: Position,
    ):
        position.x = value.x
        position.y = value.y


class SizeTransition(ObjectTransition):
    def __init__(
        self,
        *,
        speed: float | None = None,
        duration: float | None = 1,
        skip: float | None = None,
        easing=Easing.linear,
    ):
        super().__init__(speed=speed, duration=duration, skip=skip, easing=easing)

    def selector(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: object | None,
    ) -> Size:
        return size

    def setter(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: object | None,
        value: Size,
    ):
        size.width = value.width
        size.height = value.height


class FillTransition(ObjectTransition):
    def __init__(
        self,
        *,
        speed: float | None = None,
        duration: float | None = 1,
        skip: float | None = None,
        easing=Easing.linear,
    ):
        super().__init__(speed=speed, duration=duration, skip=skip, easing=easing)

    def selector(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
    ) -> Transitionable:
        if state is None or not hasattr(state, "fill"):
            raise Exception(
                "FillTransition component must be on an entity which supports fill"
            )

        return state.fill

    def setter(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: Any | None,
        value: Transitionable,
    ):
        if state is None or not hasattr(state, "fill"):
            raise Exception(
                "FillTransition component must be on an entity which supports fill"
            )

        state.fill = value


class SizeLayoutTransition(ObjectLayoutTransition):
    def __init__(
        self,
        *,
        speed: float | None = None,
        duration: float | None = 1,
        skip: float | None = None,
        easing=Easing.linear,
    ):
        super().__init__(speed=speed, duration=duration, skip=skip, easing=easing)

    def selector(self, entity: Entity, ctx: FrameContext, state: Any | None) -> Size:
        if state is None:
            raise Exception(f"State must be set on {entity}")

        return state.size

    def setter(self, entity: Entity, ctx: FrameContext, state: Any | None, value: Size):
        if state is None:
            raise Exception(f"State must be set on {entity}")

        state.size.width = value.width
        state.size.height = value.height


class SquareShake(Component):
    def __init__(
        self, *, x_spread: float = 10, y_spread: float = 10, each: float = 0.1
    ):
        self.x_spread = x_spread
        self.y_spread = y_spread
        self.each = each
        self.remaining_time = each
        self.offset_x = 0
        self.offset_y = 0

    def before_paint(
        self,
        entity: Entity,
        ctx: FrameContext,
        position: Position,
        size: Size,
        state: object | None,
    ):
        self.each -= ctx.delta_time
        if self.each <= 0:
            self.offset_x = random() * self.x_spread - self.x_spread / 2
            self.offset_y = random() * self.y_spread - self.y_spread / 2
            self.each = self.remaining_time

        position.x += self.offset_x
        position.y += self.offset_y


class SetCursor(Component):
    def __init__(self, *, cursor="hand2", tag: str = ""):
        self.cursor = cursor
        self.tag = tag

    def create(self, entity):
        self.entity = entity
        self.tag = self.tag or entity.id
        self.enter_id = entity.canvas.tag_bind(self.tag, "<Enter>", self.enter, add="+")
        self.leave_id = entity.canvas.tag_bind(self.tag, "<Leave>", self.leave, add="+")

    def destroy(self, entity: Entity):
        self.entity.canvas.tag_unbind(self.tag, "<Enter>", self.enter_id)
        self.entity.canvas.tag_unbind(self.tag, "<Leave>", self.leave_id)

    def enter(self, e):
        self.entity.canvas.config(cursor=self.cursor)

    def leave(self, e):
        self.entity.canvas.config(cursor="")
