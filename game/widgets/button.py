import random

from collections.abc import Callable
from tkinter.font import Font
from typing import Literal
from engine.animation.utils import Easing
from engine.entities.basic import Entity, Rect, Text
from engine.entities.components.base import Component
from engine.entities.components.effects import FillTransition, SetCursor
from engine.entities.components.events import OnClick
from engine.entities.layout import Center, Padding
from engine.models import EdgeInset
from game.theme_colors import ThemeColors


class ButtonHover(Component):
    def __init__(self, tag: str = ""):
        self.tag = tag

    def create(self, entity: Entity):
        self.entity = entity
        self.original_fill = entity.state.fill
        self.original_text_fill = entity.child.child.child.state.fill  # type: ignore
        self.tag = self.tag or entity.id
        self.enter_id = self.entity.canvas.tag_bind(
            self.tag, "<Enter>", self.on_mouse_enter, add="+"
        )
        self.leave_id = self.entity.canvas.tag_bind(
            self.tag, "<Leave>", self.on_mouse_leave, add="+"
        )

    def destroy(self, entity: Entity):
        self.entity.canvas.tag_unbind(self.tag, "<Enter>", self.enter_id)
        self.entity.canvas.tag_unbind(self.tag, "<Leave>", self.leave_id)
        self.on_mouse_leave(None)

    def on_mouse_enter(self, e):
        self.entity.state.fill = ThemeColors.fg()
        self.entity.child.child.child.state.fill = ThemeColors.fg_inverse()  # type: ignore

    def on_mouse_leave(self, e):
        self.entity.state.fill = self.original_fill
        self.entity.child.child.child.state.fill = self.original_text_fill  # type: ignore


class Button:
    @staticmethod
    def build(
        *,
        tag: str | None = None,
        title: str,
        fill=ThemeColors.primary(),
        on_click: Callable | None = None,
        font: Font | None = None,
        size: Literal["sm", "md", "lg"] = "md",
    ) -> Entity:
        tag = tag or random.randbytes(16).hex()

        padding = (40, 20) if size == "lg" else (20, 10) if size == "md" else (10, 5)
        font_size = 18 if size == "lg" else 14 if size == "md" else 12

        return Rect(
            tag=tag,
            fill=fill,
            components=[
                *([OnClick(tag=tag, callback=on_click)] if on_click else []),
                SetCursor(cursor="hand1", tag=tag),
                ButtonHover(tag=tag),
                FillTransition(duration=0.2, easing=Easing.ease_in_out),
            ],
            child=Padding(
                padding=EdgeInset.symmetric(padding[0], padding[1]),
                child=Center(
                    child=Text(
                        tag=tag,
                        text=title,
                        fill=ThemeColors.fg(),
                        font=font
                        or Font(
                            family="Arial",
                            size=font_size,
                            weight="bold",
                        ),
                        components=[
                            FillTransition(duration=0.2, easing=Easing.ease_in_out)
                        ],
                    )
                ),
            ),
        )
