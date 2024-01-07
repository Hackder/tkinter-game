from __future__ import annotations
from typing import Literal


class PlayerState:
    def __init__(self, i: int):
        self.name = f"Player {i + 1}"
        self.character = ""

    name: str = ""
    character: str = ""


class GameState:
    players: list[PlayerState] = []

    def create_players(self, n: int):
        self.players = [PlayerState(i) for i in range(n)]
        State.set_new_game_section("view_characters")


class State:
    Scene = Literal["menu", "new_game", "game"]
    scene: str = "menu"

    @staticmethod
    def set_scene(scene: State.Scene):
        State.scene = scene

    NewGameSection = Literal["choose_n_players", "view_characters"]
    new_game_section: Literal[
        "choose_n_players", "view_characters"
    ] = "choose_n_players"

    @staticmethod
    def set_new_game_section(section: State.NewGameSection):
        State.new_game_section = section

    game = GameState()
