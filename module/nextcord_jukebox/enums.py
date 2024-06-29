from enum import Enum, unique


@unique
class loop_mode(Enum):
    """
    Enum representing the different loop modes for a music player.

    Attributes:
        off (int): Loop mode is off, meaning no repeat.
        single (int): Loop mode for repeating the current song.
        all (int): Loop mode for repeating all songs in the queue.
    """

    off = 1
    single = 2
    all = 3
