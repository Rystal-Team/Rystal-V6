#  ------------------------------------------------------------
#  Copyright (c) 2024 Rystal-Team
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#  ------------------------------------------------------------
#

import random
from enum import Enum


class RouletteResult(Enum):
    ZEROS = 1
    RED = 2
    BLACK = 3
    LOST = 4


class Roulette:
    def __init__(self):
        self.Wheel = [
            "Green 0",
            "Black 28",
            "Red 9",
            "Black 26",
            "Red 30",
            "Black 11",
            "Red 7",
            "Black 20",
            "Red 32",
            "Black 17",
            "Red 5",
            "Black 22",
            "Red 34",
            "Black 15",
            "Red 3",
            "Black 24",
            "Red 36",
            "Black 13",
            "Red 1",
            "Green 00",
            "Red 27",
            "Black 10",
            "Red 25",
            "Black 29",
            "Red 12",
            "Black 8",
            "Red 19",
            "Black 31",
            "Red 18",
            "Black 6",
            "Red 21",
            "Black 33",
            "Red 16",
            "Black 4",
            "Red 23",
            "Black 35",
            "Red 14",
            "Black 2",
        ]

    def spin_wheel(self):
        return random.choice(self.Wheel)

    @staticmethod
    def check_winner(result, option):
        if result[0].lower() == option[0].lower() and result[0].lower() == "g":
            return RouletteResult.ZEROS, result
        if result[0].lower() == option[0].lower() and result[0].lower() == "r":
            return RouletteResult.RED, result
        if result[0].lower() == option[0].lower() and result[0].lower() == "b":
            return RouletteResult.BLACK, result
        return RouletteResult.LOST, result
