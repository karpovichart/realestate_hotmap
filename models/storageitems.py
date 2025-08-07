from models.coords import Coords


class StorageItem:
    coords: Coords
    price: int

    def __init__(self, coords: Coords, price: int) -> None:
        self.coords = coords
        self.price = price

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StorageItem):
            return self.price.__eq__(other.price) and self.coords.__eq__(other.coords)
        else:
            return False
