import time
from math import inf


class CountTimer:
    def __init__(self, duration=0):
        self._time_started = None
        self._timepaused = None
        self._elapsed = 0
        self.paused = True
        self.duration = duration

    def reset(self, duration=0):
        self.__init__(duration)

    def start(self):
        if self._time_started:
            return
        self._time_started = time.time()
        self.paused = False

    def pause(self):
        if self.paused or self._time_started is None:
            return
        self._timepaused = time.time()
        self.paused = True

    def resume(self):
        if not self.paused or self._time_started is None:
            return

        pauseduration = time.time() - self._timepaused
        self._time_started = self._time_started + pauseduration
        self.paused = False

    def _get(self):
        if not self._time_started:
            return 0
        if self.paused:
            return self._timepaused - self._time_started
        else:
            return time.time() - self._time_started

    @property
    def running(self) -> bool:
        return not self.paused

    @property
    def expired(self) -> bool:
        return self.elapsed >= self.duration and self.duration != 0

    @property
    def elapsed(self) -> float:
        got = self._get()
        return got or 0

    @property
    def remaining(self) -> float:
        got = self._get()
        time_left = self.duration - got if self.duration else inf
        return max(time_left, 0)
