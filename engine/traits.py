from __future__ import annotations
from abc import ABC, abstractmethod


class Transitionable[T](ABC):
    @abstractmethod
    def distance(self, other: T) -> float:
        pass

    @abstractmethod
    def copy(self) -> T:
        pass

    @abstractmethod
    def interpolate(self, other: T, progress: float) -> T:
        pass
