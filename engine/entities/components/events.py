from dataclasses import dataclass
from tkinter import Event
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


@dataclass(frozen=True)
class DragEvent:
    event: Event

    total_dx: int
    total_dy: int

    dx: int
    dy: int


class OnDrag(Component):
    def __init__(self, *, tag: None | str = None, drag: Callable):
        self.drag = drag
        self.tag = tag
        self.dragging = False

    def create(self, entity: Entity):
        self.entity = entity
        id_tag = self.tag or self.entity.id
        self.event_id = self.entity.canvas.tag_bind(
            id_tag, "<B1-Motion>", self.on_drag, add="+"
        )
        self.mouse_down_event_id = self.entity.canvas.tag_bind(
            id_tag, "<Button-1>", self.on_mouse_down, add="+"
        )

    def destroy(self, entity: Entity):
        id_tag = self.tag or self.entity.id
        self.entity.canvas.tag_unbind(id_tag, "<B1-Motion>", self.event_id)

    def on_drag(self, e):
        event = DragEvent(
            e,
            e.x - self.start[0],
            e.y - self.start[1],
            e.x - self.last[0],
            e.y - self.last[1],
        )
        self.last = (e.x, e.y)

        self.drag(event, self.entity)

    def on_mouse_down(self, e):
        self.start = (e.x, e.y)
        self.last = (e.x, e.y)
        self.dragging = True
