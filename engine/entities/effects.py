from __future__ import annotations
from random import random
from abc import ABC, abstractmethod
from engine.models import Position, DefinedSize, FrameContext
from engine.traits import Transitionable
from engine.animation.utils import Easing
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from engine.entities.basic import Entity

class Effect(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None):
        pass

class LayoutEffect(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process(self, entity: Entity, ctx: FrameContext, state):
        pass

class ObjectTransition(Effect, ABC):
    def __init__(self, *,
                 speed: float|None = None,
                 duration: float|None = 1,
                 skip: float|None = None,
                 easing = Easing.linear):
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
    def selector(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None) -> Transitionable:
        pass

    @abstractmethod
    def setter(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None, value: Transitionable):
        pass

    def process(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None):
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
            raise Exception('Either speed or duration must be set')

        self.progress = min(self.progress, 1)

        self.value = self.last_value.interpolate(self.target_value, self.easing(self.progress))

        self.setter(entity, ctx, position, size, state, self.value)


class PositionTransition(ObjectTransition):
    def __init__(self, *,
                 speed: float|None = None,
                 duration: float|None = 1,
                 skip: float|None = None,
                 easing = Easing.linear):
        super().__init__(speed=speed, duration=duration, skip=skip, easing=easing)

    def selector(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None) -> Position:
        return position

    def setter(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None, value: Position):
        position.x = value.x
        position.y = value.y

class SizeTransition(ObjectTransition):
    def __init__(self, *,
                 speed: float|None = None,
                 duration: float|None = 1,
                 skip: float|None = None,
                 easing = Easing.linear):
        super().__init__(speed=speed, duration=duration, skip=skip, easing=easing)

    def selector(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None) -> DefinedSize:
        return size

    def setter(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None, value: DefinedSize):
        size.width = value.width
        size.height = value.height

class SquareShake(Effect):
    def __init__(self, *, x_spread: float=10, y_spread: float=10, each: float=0.1):
        self.x_spread = x_spread
        self.y_spread = y_spread
        self.each = each
        self.remaining_time = each
        self.offset_x = 0
        self.offset_y = 0

    def process(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize, state: object | None):
        self.each -= ctx.delta_time
        if self.each <= 0:
            self.offset_x = random() * self.x_spread - self.x_spread / 2
            self.offset_y = random() * self.y_spread - self.y_spread / 2
            self.each = self.remaining_time

        position.x += self.offset_x
        position.y += self.offset_y

