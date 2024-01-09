from typing import Callable
from multiprocessing import Process

from engine.entities.layout import (
    Padding,
    Flex,
    SizeBox,
    Expanded,
    FlexDirection,
    Alignment,
)
from engine.entities.basic import Entity
from engine.models import EdgeInset
from game.state import State
from game.widgets.button import Button


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
    def build():
        menu_entries = [
            MenuEntry(
                "New Game",
                lambda *_: State.set_scene("new_game"),
            ),
            MenuEntry("Load Game", MainMenu.load_game),
        ]

        return Padding(
            padding=EdgeInset.all(50),
            child=Flex(
                direction=FlexDirection.Row,
                children=[
                    Expanded(),
                    SizeBox(
                        width=240,
                        child=Flex(
                            direction=FlexDirection.Column,
                            align=Alignment.Stretch,
                            gap=20,
                            children=[
                                Expanded(),
                                *[
                                    Button.build(
                                        title=entry.title,
                                        size="lg",
                                        on_click=entry.on_click,
                                    )
                                    for entry in menu_entries
                                ],
                                Button.build(
                                    title="Quit", size="lg", on_click=lambda *_: exit()
                                ),
                                Expanded(),
                            ],
                        ),
                    ),
                    Expanded(),
                ],
            ),
        )
