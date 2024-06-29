import time
from math import inf


class CountTimer:
    def __init__(self, duration=0):
        """
        This Python function initializes a timer object with specified duration and default values for
        time-related attributes.

        :param duration: The `duration` parameter in the `__init__` method of the class is used to
        specify the total duration of the timer in seconds. It is set to 0 by default if no value is
        provided when creating an instance of the class, defaults to 0 (optional)
        """
        self._time_started = None
        self._timepaused = None
        self._elapsed = 0
        self.paused = True
        self.duration = duration

    def reset(self, duration=0):
        """
        The `reset` function in Python reinitializes an object with an optional duration parameter.

        :param duration: The `duration` parameter in the `reset` method is used to specify the duration
        for which the object should be reset. If a duration is provided, the object will be reset with
        that duration, otherwise, it will be reset with a default duration of 0, defaults to 0
        (optional)
        """
        self.__init__(duration)

    def start(self):
        """
        The `start` function initializes a timer if it has not already been started.

        :return: If `start` is called and `self._time_started` is already set, then the function will
        reset the time start value and start over.
        """
        self._time_started = time.time()
        self.paused = False

    def pause(self):
        """
        The function `pause` checks if the object is already paused or if the time started is not set,
        and if not, it records the time paused and sets the object as paused.

        :return: If the conditions in the `if` statement are met (i.e., `self.paused` is already `True`
        or `self._time_started` is `None`), then nothing is being returned. The function will exit
        without returning anything in that case.
        """
        if self.paused or self._time_started is None:
            return
        self._timepaused = time.time()
        self.paused = True

    def resume(self):
        """
        This Python function resumes a timer by adjusting the start time based on the duration it was
        paused.

        :return: If the conditions are met (self.paused is False or self._time_started is None), nothing
        will be returned.
        """
        if not self.paused or self._time_started is None:
            return

        # The line `pauseduration = time.time() - self._timepaused` in the `resume` method of the
        # `CountTimer` class is calculating the duration for which the timer was paused.
        pauseduration = time.time() - self._timepaused
        self._time_started = self._time_started + pauseduration
        self.paused = False

    def _get(self):
        """
        This function calculates the elapsed time based on the start time and whether the timer is
        paused.

        :return: The method `_get` returns the elapsed time in seconds based on the conditions specified
        in the code snippet. If the timer has not been started (`self._time_started` is not set), it
        returns 0. If the timer is paused (`self.paused` is True), it returns the difference between the
        paused time (`self._timepaused`) and the time the timer was started (`self._time
        """
        if not self._time_started:
            return 0
        if self.paused:
            return self._timepaused - self._time_started
        else:
            return time.time() - self._time_started

    @property
    def running(self) -> bool:
        """
        The function `running` returns `True` if the object is not paused, and `False` otherwise.

        :return: The `running` method is returning the opposite of the `paused` attribute of the object.
        It returns `True` if the object is not paused, and `False` if it is paused.
        """
        return not self.paused

    @property
    def expired(self) -> bool:
        """
        The function `expired` returns `True` if the elapsed time is greater than or equal to the
        duration and the duration is not zero.
        :return: The `expired` method is returning a boolean value. It checks if the elapsed time is
        greater than or equal to the duration and if the duration is not equal to 0. If both conditions
        are met, it returns `True`, indicating that the object has expired. Otherwise, it returns
        `False`.
        """
        return self.elapsed >= self.duration and self.duration != 0

    @property
    def elapsed(self) -> float:
        """
        The `elapsed` function returns the value obtained from `_get` method or 0 if the value is None.

        :return: The `elapsed` method is returning the value of `got` if it is not None, otherwise it
        returns 0.
        """
        got = self._get()
        return got or 0

    @property
    def remaining(self) -> float:
        """
        This Python function calculates the remaining time based on the duration and the time already
        elapsed.

        :return: The `remaining` method is returning the maximum value between the time left (calculated
        as the difference between the duration and the time already spent) and 0. This ensures that the
        method always returns a non-negative value representing the remaining time.
        """
        got = self._get()
        time_left = self.duration - got if self.duration else inf
        return max(time_left, 0)
