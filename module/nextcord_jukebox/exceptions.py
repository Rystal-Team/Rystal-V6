"""
Custom exceptions for the Nextcord Jukebox application.
"""


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

class NextcordJukeBoxError(Exception):
    """Base Nextcord Jukebox Exception."""

    def __str__(self):
        return self.__doc__


class QueueError(NextcordJukeBoxError):
    """Queue related function error."""

    def __str__(self):
        return self.__doc__


class PlayError(NextcordJukeBoxError):
    """Play related function errored."""

    def __str__(self):
        return self.__doc__


class FailedConnection(NextcordJukeBoxError):
    """Failed to connect to a voice channel."""

    def __str__(self):
        return self.__doc__


class UserNotConnected(PlayError):
    """The user is not connected to a voice channel."""

    def __str__(self):
        return self.__doc__


class VoiceChannelMismatch(PlayError):
    """The user is connected to a different voice channel as the bot."""

    def __str__(self):
        return self.__doc__


class NotConnected(PlayError):
    """The bot is not connected to a voice channel."""

    def __str__(self):
        return self.__doc__


class LoadingStream(PlayError):
    """The player is loading stream already, please slow down."""

    def __str__(self):
        return self.__doc__


class NotPlaying(PlayError):
    """Not playing music."""

    def __str__(self):
        return self.__doc__


class NothingPlaying(PlayError):
    """Nothing is playing."""

    def __str__(self):
        return self.__doc__


class AlreadyPaused(PlayError):
    """The music is already paused."""

    def __str__(self):
        return self.__doc__


class NotPaused(PlayError):
    """The music is not paused."""

    def __str__(self):
        return self.__doc__


class NoQueryResult(PlayError):
    """Query has no results returned."""

    def __str__(self):
        return self.__doc__


class EmptyQueue(QueueError):
    """There is nothing in the queue."""

    def __str__(self):
        return self.__doc__
