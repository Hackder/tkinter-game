from __future__ import annotations
import random
from typing import Literal


class Character:
    def __init__(self, *, idle_asset_key: str, walk_asset_key: str):
        self.idle_asset_key = idle_asset_key
        self.walk_asset_key = walk_asset_key

    @staticmethod
    def all() -> list[Character]:
        return [
            Character(
                idle_asset_key=f"character{i}-idle",
                walk_asset_key=f"character{i}-walk",
            )
            for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        ]


class PlayerState:
    def __init__(self, i: int, character: Character, human: bool = True):
        if human:
            self.name = f"Player {i + 1}"
        else:
            self.name = f"Bot {i + 1}"
        self.character = character
        self.human = human
        self.revealed_times = 0


class GameState:
    players: list[PlayerState] = []

    def create_players(self, n: int):
        chars = random.sample(Character.all(), k=2 * n)

        self.players = [PlayerState(i, chars[i]) for i in range(n)]
        self.players.extend([PlayerState(i, chars[n + i], False) for i in range(n)])
        State.set_new_game_section("view_characters")

    def humans(self):
        return filter(lambda p: p.human, self.players)


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

    shown_player: PlayerState | None = None

    @staticmethod
    def toggle_shown_player(p: PlayerState):
        if State.shown_player == p:
            State.shown_player = None
            return

        State.shown_player = p
        p.revealed_times += 1

    game = GameState()
