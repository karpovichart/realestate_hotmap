class Coords:  # todo create compare
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Coords):
            return self.x.__eq__(other.x) and self.y.__eq__(other.y)
        else:
            return False
