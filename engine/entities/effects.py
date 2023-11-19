from __future__ import annotations
from random import random
from abc import ABC, abstractmethod
from engine.models import Position, DefinedSize, FrameContext
from engine.animation.utils import Easing
from timeit import default_timer as timer
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.entities.basic import Entity

class Effect(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize | None, state: object | None):
        pass

class LayoutEffect(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process(self, entity: Entity, ctx: FrameContext, state):
        pass

class PositionTransition(Effect):
    def __init__(self, *, speed: float|None = None, duration: float|None = 1, easing = Easing.linear):
        self.speed = speed
        self.duration = duration
        self.last_position = None
        self.target_position = None
        self.position = None
        self.progress = 0
        self.distance = 0
        self.easing = easing

    def process(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize | None, state: object | None):
        if self.last_position is None or self.position is None or self.target_position is None:
            self.last_position = position
            self.target_position = position
            self.position = position
            return

        if position != self.target_position:
            self.last_position = self.position
            self.target_position = position.copy()
            self.distance = position.distance(self.last_position)
            self.progress = 0

        if self.progress == 1 or self.distance == 0:
            return

        if self.speed is not None:
            self.progress += self.speed / self.distance * ctx.delta_time
        elif self.duration is not None:
            self.progress += ctx.delta_time / self.duration
        else:
            raise Exception('Either speed or duration must be set')

        self.progress = min(self.progress, 1)

        self.position = self.last_position.lerp(self.target_position, self.easing(self.progress))

        position.x = self.position.x
        position.y = self.position.y
        

class SquareShake(Effect):
    def __init__(self, *, x_spread: float=10, y_spread: float=10, each: float=0.1):
        self.x_spread = x_spread
        self.y_spread = y_spread
        self.each = each
        self.remaining_time = each
        self.offset_x = 0
        self.offset_y = 0

    def process(self, entity: Entity, ctx: FrameContext, position: Position, size: DefinedSize | None, state: object | None):
        self.each -= ctx.delta_time
        if self.each <= 0:
            self.offset_x = random() * self.x_spread - self.x_spread / 2
            self.offset_y = random() * self.y_spread - self.y_spread / 2
            self.each = self.remaining_time

        position.x += self.offset_x
        position.y += self.offset_y

