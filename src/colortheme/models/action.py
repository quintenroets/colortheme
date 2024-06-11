from enum import Enum


class Action(str, Enum):
    check = "check"
    dark = "dark"
    light = "light"
    restart = "restart"
