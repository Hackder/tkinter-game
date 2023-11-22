from engine.entities.components.base import Component
from engine.entities.basic import Entity
from engine.models import FrameContext, Position, Size
from typing import Any
from timeit import default_timer as timer


class FpsCounter(Component):
    def __init__(self, period: int = 10):
        self.period = period
        self.frames_passed = 0
        self.text = "Calculating..."

    def create(self, entity):
        self.start_time = timer()

    def before_layout(self, entity: Entity, ctx: FrameContext, state: Any | None):
        self.frames_passed += 1
        if self.frames_passed >= self.period:
            self.frames_passed = 0
            now = timer()
            self.text = f'{self.period / (now - self.start_time):.2f} fps'
            self.start_time = now

        if state is None or not hasattr(state, 'text'):
            raise Exception('FpsCounter component must be on an entity which supports text')

        state.text = self.text

class DebugBounds(Component):
    def create(self, entity):
        self.id = entity.canvas.create_rectangle(0, 0, 0, 0, outline='red', width=1)
        self.text_id = entity.canvas.create_text(0, 0, text='', fill='red', anchor='sw', font=('Arial', 10))

    def destroy(self, entity: Entity):
        entity.canvas.delete(self.id)
        entity.canvas.delete(self.text_id)

    def before_paint(self, entity: Entity, ctx: FrameContext, position: Position, size: Size, state: Any | None):
        entity.canvas.coords(self.id, position.x, position.y, position.x + size.width, position.y + size.height)
        entity.canvas.coords(self.text_id, position.x, position.y)
        entity.canvas.itemconfig(self.text_id, text=f'{entity.__class__.__name__} (tag={entity.tag}) {size.width:.2f}x{size.height:.2f}')
