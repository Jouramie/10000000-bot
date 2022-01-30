from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __lt__(self, other) -> bool:
        return (self.y, self.x) < (other.y, other.x)

    def __mul__(self, other):
        if isinstance(other, int):
            return Point(self.x * other, self.y * other)
        raise NotImplementedError()

    def __add__(self, other):
        if type(self) is type(other):
            return Point(self.x + other.x, self.y + other.y)
        raise NotImplementedError()

    def __sub__(self, other):
        if type(self) is type(other):
            return Point(self.x - other.x, self.y - other.y)
        raise NotImplementedError()

    def __str__(self):
        return str((self.x, self.y))

    def distance_between(self, other) -> int:
        return int(sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2))


@dataclass(frozen=True)
class ScreenSquare:
    left: int = 0
    top: int = 0
    height: int = 0
    width: int = 0

    def __lt__(self, other) -> bool:
        return (self.top, self.left) < (other.top, other.left)

    def find_center(self) -> Point:
        return Point(self.left + int(self.width / 2), self.top + int(self.height / 2))
