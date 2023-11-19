from abc import ABC, abstractmethod
from engine.models import Position, DefinedSize, FrameContext

class Effect(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process(self, ctx: FrameContext, position: Position, size: DefinedSize | None, state: object | None):
        pass

class LayoutEffect(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process(self, ctx: FrameContext, state):
        pass
