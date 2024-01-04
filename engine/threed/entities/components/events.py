from typing import Callable
from engine.threed.entities.basic import Entity3d
from engine.threed.entities.components.base import Component3d


class OnClick(Component3d):
    def __init__(self, callback: Callable, tag: str):
        self.callback = callback
        self.tag = tag
        self.event_ids = []

    def create(self, entity: Entity3d):
        self.entity = entity
        if self.tag:
            id = self.entity.canvas.tag_bind(
                self.tag, "<Button-1>", self.on_click, add="+"
            )
            self.event_ids.append(id)
        else:
            for id in entity.ids:
                event_id = self.entity.canvas.tag_bind(
                    id, "<Button-1>", self.on_click, add="+"
                )
                self.event_ids.append(event_id)

    def destroy(self):
        if self.tag:
            for id in self.event_ids:
                self.entity.canvas.tag_unbind(self.tag, "<Button-1>", id)

        for entity_id, id in zip(self.entity.ids, self.event_ids):
            self.entity.canvas.tag_unbind(entity_id, "<Button-1>", id)

    def on_click(self, e):
        self.callback(e, self.entity)
