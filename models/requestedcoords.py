from typing import List, Any

from models.coords import Coords


class RequestedCoords:
    coords: List[Coords]

    def __init__(self) -> None:
        self.coords = []

    def get_last(self) -> Coords | list[Any]:
        if self.count():
            return self.coords[-1]
        else:
            return []

    def delete_last(self) -> None:
        if self.count():
            self.coords.pop()

    def count(self) -> int:
        return len(self.coords)
