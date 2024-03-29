from __future__ import annotations
import pickle
from dataclasses import dataclass
import random
from typing import Literal
from engine.models import Position
from game.logger import logger

from game.board_generator import BoardGenerator


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
        self.x = 2
        self.y = 2


@dataclass
class RoomState:
    x: int
    y: int
    width: int
    height: int


class GameState:
    players: list[PlayerState] = []
    board: list[RoomState] = []
    start_room: RoomState | None = None
    end_room: RoomState | None = None
    scale: float = 50
    available_steps: int | None = None
    turn: int = 0
    current_action: Literal["throw_dice", "move"] = "throw_dice"
    winner: PlayerState | None = None

    def create_players(self, n: int):
        chars = random.sample(Character.all(), k=2 * n)

        self.players = [PlayerState(i, chars[i]) for i in range(n)]
        self.players.extend([PlayerState(i, chars[n + i], False) for i in range(n)])
        State.set_new_game_section("view_characters")

    def humans(self):
        return filter(lambda p: p.human, self.players)

    def generate_board(self):
        generator = BoardGenerator(5, range(-25, 20))
        board = generator.generate_board(7)

        self.board = []
        for room in board:
            self.board.append(RoomState(*room, 5, 5))

        self.start_room = self.board[0]
        self.end_room = self.board[-1]

    def next_turn(self):
        self.turn = (self.turn + 1) % len(list(self.humans()))
        self.current_action = "throw_dice"
        self.available_steps = None

    def current_player(self) -> PlayerState:
        return self.players[self.turn]

    def dice_throw(self, n):
        self.available_steps = n
        self.current_action = "move"

    def player_moved(self, p: PlayerState):
        assert self.end_room is not None

        if self.is_in_end_room(p.x, p.y) and p.human:
            self.winner = p
            return

        self.next_turn()

    def current_action_text(self) -> str:
        if self.current_action == "throw_dice":
            return "Throw dice"
        if self.current_action == "move":
            return f"Move ({self.available_steps} steps available)"
        return "Unknown"

    def is_in_end_room(self, x: int, y: int) -> bool:
        if self.end_room is None:
            return False

        return (
            self.end_room.x <= x < self.end_room.x + self.end_room.width
            and self.end_room.y <= y < self.end_room.y + self.end_room.height
        )

    def is_in_start_room(self, x: int, y: int) -> bool:
        if self.start_room is None:
            return False

        return (
            self.start_room.x <= x < self.start_room.x + self.start_room.width
            and self.start_room.y <= y < self.start_room.y + self.start_room.height
        )


class State:
    log = logger.getChild("State")
    Scene = Literal["menu", "new_game", "game", "view_board"]
    scene: str = "menu"

    @staticmethod
    def set_scene(scene: State.Scene):
        State.log.info("Scene: %s", scene)
        if scene == "new_game":
            State.game = GameState()
            State.new_game_section = "choose_n_players"
            State.game_paused = False
            State.shown_player = None
        State.scene = scene

    NewGameSection = Literal["choose_n_players", "view_characters", "view_board"]
    new_game_section: State.NewGameSection = "choose_n_players"

    @staticmethod
    def set_new_game_section(section: State.NewGameSection):
        State.log.info("New game section: %s", section)
        State.new_game_section = section

    shown_player: PlayerState | None = None

    @staticmethod
    def toggle_shown_player(p: PlayerState):
        State.log.info("Toggle shown player: %s", p.name)
        if State.shown_player == p:
            State.shown_player = None
            return

        State.shown_player = p
        p.revealed_times += 1

    game = GameState()

    @staticmethod
    def save_game(path: str):
        State.log.info("Saving game: %s", path)
        if path == "":
            return

        save = pickle.dumps(State.game)
        with open(path, "wb") as f:
            f.write(save)

    @staticmethod
    def load_save(path: str):
        State.log.info("Loading save: %s", path)
        if path == "":
            return

        try:
            with open(path, "rb") as f:
                save = f.read()
            State.game = pickle.loads(save)
            State.set_scene("game")
        except Exception as e:
            State.log.exception(e)
            State.log.error("Failed to load save: %s", path)

    game_view_offset = Position.zero()

    @staticmethod
    def move_game_view(dx: int, dy: int):
        State.game_view_offset.mut_add((dx, dy))

    game_paused = False

    @staticmethod
    def toggle_game_paused():
        State.log.info("Toggle game paused")
        State.game_paused = not State.game_paused

    hovered_player: PlayerState | None = None

    @staticmethod
    def set_hovered_player(p: PlayerState | None):
        State.hovered_player = p

    selected_player: PlayerState | None = None

    @staticmethod
    def toggle_selected_player(p: PlayerState):
        State.log.info("Toggle selected player: %s", p.name)
        if State.game.current_action != "move":
            State.selected_player = None
            State.log.info("Not in move action, ignoring toggle_selected_player")
            return

        State.log.info("In move action, toggling selected player: %s", p.name)

        if State.selected_player == p:
            State.selected_player = None
        else:
            State.selected_player = p

    @staticmethod
    def move_selected_player_to(x: int, y: int):
        State.log.info(
            "Move selected player: %s to: (%s, %s)",
            State.selected_player.name if State.selected_player is not None else "None",
            x,
            y,
        )
        if State.selected_player is None:
            return

        State.selected_player.x = x
        State.selected_player.y = y
        State.game.player_moved(State.selected_player)
        State.selected_player = None

    _last_board: list[RoomState] | None = None
    _tile_position_array: list[list[bool]] | None = None
    _tile_position_y_offset: int = 0

    @staticmethod
    def get_tile_position_array() -> list[list[bool]]:
        if (
            State.game.board == State._last_board
            and State._tile_position_array is not None
        ):
            return State._tile_position_array

        State._last_board = State.game.board

        min_x = min(room.x for room in State.game.board)
        min_y = min(room.y for room in State.game.board)
        max_x = max(room.x + room.width for room in State.game.board)
        max_y = max(room.y + room.height for room in State.game.board)

        State._tile_position_y_offset = min_y

        State._tile_position_array = [
            [False for _ in range(min_x, max_x)] for _ in range(min_y, max_y)
        ]

        for room in State.game.board:
            for x in range(room.x, room.x + room.width):
                for y in range(room.y, room.y + room.height):
                    State._tile_position_array[y - min_y][x - min_x] = True

        return State._tile_position_array

    @staticmethod
    def is_position_in_board(x: int, y: int):
        positions = State.get_tile_position_array()
        y -= State._tile_position_y_offset

        if y < 0 or y >= len(positions):
            return False
        if x < 0 or x >= len(positions[y]):
            return False

        return positions[y][x]

    metrics = False

    _last_players: list[PlayerState] | None = None
    _shuffled_players: list[PlayerState] | None = None

    @staticmethod
    def shuffled_players() -> list[PlayerState]:
        if (
            State._last_players == State.game.players
            and State._shuffled_players is not None
        ):
            return State._shuffled_players

        if State.game.players is None:
            return []

        State._shuffled_players = random.sample(
            State.game.players, len(State.game.players)
        )
        State._last_players = State.game.players
        return State._shuffled_players

    @staticmethod
    def continue_game():
        State.log.info("Continue game")
        State.game.winner = None
