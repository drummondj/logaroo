from enum import Enum


class Level(Enum):
    """
    Enum representing different logging levels.
    """

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        return self.name
