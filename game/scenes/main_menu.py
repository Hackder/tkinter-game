from typing import Callable
from tkinter.font import Font
from multiprocessing import Process
from threading import Thread

from engine.animation.utils import Easing
from engine.entities.components.base import Component
from engine.entities.components.effects import FillTransition, SetCursor
from engine.entities.components.events import OnClick
from engine.entities.layout import (
    Padding,
    Flex,
    WidthBox,
    Expanded,
    Center,
    FlexDirection,
    Alignment,
)
from engine.entities.basic import Rect, Text, Entity
from engine.models import Color, EdgeInset


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

    def on_mouse_enter(self, e):
        self.entity.state.fill = Color.white()
        self.entity.child.child.child.state.fill = Color.black()  # type: ignore

    def on_mouse_leave(self, e):
        self.entity.state.fill = self.original_fill
        self.entity.child.child.child.state.fill = self.original_text_fill  # type: ignore


class MenuEntry:
    def __init__(self, title: str, on_click: Callable | None = None):
        self.title = title
        self.on_click = on_click


class MainMenu:
    @staticmethod
    def callback(path):
        print("path", path)

    @staticmethod
    def load_game(e, entity: Entity):
        from engine.dialogs import Dialogs

        Process(target=Dialogs.open_file_dialog, args=(MainMenu.callback,)).start()

    @staticmethod
    def menu_button(title: str, on_click: Callable | None = None):
        return Rect(
            tag=title,
            fill=Color.from_hex("#44345B"),
            components=[
                # menu_button is called only once on creation, therefore we don't
                # need to worry about lifecycle methods of conditional components (on_create, on_destroy)
                *([OnClick(on_click)] if on_click else []),
                SetCursor(cursor="hand1", tag=title),
                ButtonHover(tag=title),
                FillTransition(duration=0.2, easing=Easing.ease_in_out),
            ],
            child=Padding(
                padding=EdgeInset.symmetric(40, 20),
                child=Center(
                    child=Text(
                        tag=title,
                        text=title,
                        fill=Color.from_hex("#E0E1DD"),
                        font=Font(
                            family="Arial",
                            size=18,
                            weight="bold",
                        ),
                        components=[
                            FillTransition(duration=0.2, easing=Easing.ease_in_out)
                        ],
                    )
                ),
            ),
        )

    @staticmethod
    def build():
        menu_entries = [
            MenuEntry("New Game", lambda e, entity: print(entity)),
            MenuEntry("Load Game", MainMenu.load_game),
        ]

        return Padding(
            padding=EdgeInset.all(50),
            child=Flex(
                direction=FlexDirection.Row,
                children=[
                    Expanded(),
                    WidthBox(
                        width=240,
                        child=Flex(
                            direction=FlexDirection.Column,
                            align=Alignment.Stretch,
                            gap=20,
                            children=[
                                Expanded(),
                                *[
                                    MainMenu.menu_button(entry.title, entry.on_click)
                                    for entry in menu_entries
                                ],
                                MainMenu.menu_button("Quit", lambda e, entity: exit()),
                                Expanded(),
                            ],
                        ),
                    ),
                    Expanded(),
                ],
            ),
        )
