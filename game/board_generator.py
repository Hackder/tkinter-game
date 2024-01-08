import random
from typing import Iterable


type Room = tuple[int, int]

class BoardGenerator:
    def __init__(self, room_size: int, vertical_range: range = range(-15, 10)):
        self.room_size = room_size
        self.vertical_range = vertical_range

    def generate_board(
            self,
        n_layers: int
    ) -> list[Room]:
        start = (0, 0)
        layers: list[list[Room]] = [[start]]

        for i in range(1, n_layers):
            layer: list[Room] = []
            if i < n_layers // 2:
                # rooms_in_layer = random.randint(len(layers[-1]), len(layers[-1]) + 1)
                rooms_in_layer = len(layers[-1]) + 1
                valid_positions = self.get_valid_position(layers[-1], self.room_size)
            else:
                rooms_in_layer = random.randint(len(layers[-1]) - 1, len(layers[-1]))
                if len(layers[-1]) == 1:
                    rooms_in_layer = 0
                # rooms_in_layer = max(len(layers[-1]) - 1, 1)
                valid_positions = self.get_valid_position(layers[-1], 0)

            for _ in range(rooms_in_layer):
                if len(valid_positions) == 0:
                    break

                room_position = random.choice(list(valid_positions))
                room = (i * self.room_size, room_position)
                
                room_positions = self.positions_for_room(room)
                valid_positions.difference_update(room_positions)
                before = min(room_positions) - 1
                if before in valid_positions:
                    valid_positions.remove(before)

                after = max(room_positions) + 1
                if after in valid_positions:
                    valid_positions.remove(after)

                layer.append(room)

            layers.append(layer)

        return [room for layer in layers for room in layer]

    def get_valid_position(self, rooms: list[Room], allow_expand: int):
        valid_positions: set[int] = set()

        for room in rooms:
            valid_positions.update(self.positions_for_room(room))

        if len(valid_positions) == 0:
            return valid_positions

        min_pos = min(valid_positions) + (self.room_size - allow_expand) - 1
        max_pos = max(valid_positions) - (self.room_size - allow_expand) + 1

        new_valid_positions = set()
        for pos in valid_positions:
            if pos in self.vertical_range and pos >= min_pos and pos <= max_pos:
                new_valid_positions.add(pos)

        return new_valid_positions

    def positions_for_room(self, room: Room) -> Iterable[int]:
        return range(room[1] - self.room_size + 1, room[1] + self.room_size)
