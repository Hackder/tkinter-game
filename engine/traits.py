from __future__ import annotations
from abc import ABC, abstractmethod


class Transitionable(ABC):
    @abstractmethod
    def distance(self, other: Transitionable) -> float:
        pass

    @abstractmethod
    def copy(self) -> Transitionable:
        pass

    @abstractmethod
    def interpolate(self, other: Transitionable, progress: float) -> Transitionable:
        pass
