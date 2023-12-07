from enum import Enum
from dataclasses import dataclass

class PlayerState(Enum):
    WANDER  = 1
    ESCAPE  = 2
    ATTACK  = 3
    HEAL    = 4

class ItemType(Enum):
    BOT  = 0 #us
    FOOD = 1
    ENEMY = 2
    SHELTER = 3

@dataclass
class Size:
    width: int
    height: int

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Item:
    pos: Position
    radius: float
    item_type: ItemType

@dataclass
class VisibleField:
    radius: float #todo
    items: list[Item]