from typing import Callable
from engine.entities.components.base import Component
from engine.entities.basic import Entity


class OnClick(Component):
    def __init__(self, callback: Callable):
        self.callback = callback

    def create(self, entity: Entity):
        self.entity = entity
        self.entity.canvas.tag_bind(self.entity.id, "<Button-1>", self.on_click, add="+")

    def destroy(self):
        self.entity.canvas.tag_unbind(self.entity.id, "<Button-1>")

    def on_click(self, e):
        self.callback(e, self.entity)
