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

import time
from math import inf
from typing import Optional


class CountTimer:
    """
    A class to represent a countdown timer.

    Attributes:
        duration (int): The duration of the timer in seconds.
        _time_started (Optional[float]): The time when the timer was started.
        _timepaused (Optional[float]): The time when the timer was paused.
        paused (bool): Indicates if the timer is paused.
    """

    def __init__(self, duration: int = 0) -> None:
        """
        Initialize the CountTimer with a specified duration.

        Args:
            duration (int): The duration of the timer in seconds. Default is 0.
        """
        self._time_started: Optional[float] = None
        self._timepaused: Optional[float] = None
        self.paused: bool = True
        self.duration: int = duration

    def reset(self, duration: int = 0) -> None:
        """
        Reset the timer with a new duration.

        Args:
            duration (int): The new duration of the timer in seconds. Default is 0.
        """
        self.__init__(duration)

    def start(self) -> None:
        """
        Start the timer.
        """
        self._time_started = time.time()
        self.paused = False

    def pause(self) -> None:
        """
        Pause the timer.
        """
        if not self.paused and self._time_started is not None:
            self._timepaused = time.time()
            self.paused = True

    def resume(self) -> None:
        """
        Resume the timer from a paused state.
        """
        if self.paused and self._time_started is not None:
            self._time_started += time.time() - (self._timepaused or 0)
            self._timepaused = None
            self.paused = False

    def _get(self) -> float:
        """
        Get the elapsed time since the timer started.

        Returns:
            float: The elapsed time in seconds.
        """
        if self._time_started is None:
            return 0.0
        if self.paused:
            return (self._timepaused or 0) - self._time_started
        return time.time() - self._time_started

    @property
    def running(self) -> bool:
        """
        Check if the timer is running.

        Returns:
            bool: True if the timer is running, False otherwise.
        """
        return not self.paused

    @property
    def expired(self) -> bool:
        """
        Check if the timer has expired.

        Returns:
            bool: True if the timer has expired, False otherwise.
        """
        return self.elapsed >= self.duration != 0

    @property
    def elapsed(self) -> float:
        """
        Get the elapsed time since the timer started.

        Returns:
            float: The elapsed time in seconds.
        """
        return self._get() or 0.0

    @property
    def remaining(self) -> float:
        """
        Get the remaining time until the timer expires.

        Returns:
            float: The remaining time in seconds.
        """
        time_left = self.duration - self._get() if self.duration else inf
        return max(time_left, 0.0)
