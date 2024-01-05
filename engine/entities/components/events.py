from typing import Callable
from engine.entities.components.base import Component
from engine.entities.basic import Entity


class OnClick(Component):
    def __init__(self, *, tag: None | str = None, callback: Callable):
        self.callback = callback
        self.tag = tag

    def create(self, entity: Entity):
        self.entity = entity
        id_tag = self.tag or self.entity.id
        self.event_id = self.entity.canvas.tag_bind(
            id_tag, "<Button-1>", self.on_click, add="+"
        )

    def destroy(self, entity: Entity):
        id_tag = self.tag or self.entity.id
        self.entity.canvas.tag_unbind(id_tag, "<Button-1>", self.event_id)

    def on_click(self, e):
        self.callback(e, self.entity)
