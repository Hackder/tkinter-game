from abc import ABC, abstractmethod
from tkinter import Canvas

from engine.renderer import FrameContext

class Entity(ABC):
    id = 0

    @abstractmethod
    def __init__(self, *, tag: str|None = None):
        pass

    @abstractmethod
    def construct(self, canvas: Canvas):
        pass

    @abstractmethod
    def paint(self, ctx: FrameContext):
        pass

    @abstractmethod
    def layout(self, ctx: FrameContext):
        pass
