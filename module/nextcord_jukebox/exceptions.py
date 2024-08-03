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


class QueueError(NextcordJukeBoxError):
    """Queue related function error."""


class PlayError(NextcordJukeBoxError):
    """Play related function errored."""


class FailedConnection(NextcordJukeBoxError):
    """Failed to connect to a voice channel."""


class UserNotConnected(PlayError):
    """The user is not connected to a voice channel."""


class VoiceChannelMismatch(PlayError):
    """The user is connected to a different voice channel as the bot."""


class NotConnected(PlayError):
    """The bot is not connected to a voice channel."""


class LoadingStream(PlayError):
    """The player is loading stream already, please slow down."""


class NotPlaying(PlayError):
    """Not playing music."""


class NothingPlaying(PlayError):
    """Nothing is playing."""


class AlreadyPaused(PlayError):
    """The music is already paused."""


class NotPaused(PlayError):
    """The music is not paused."""


class NoQueryResult(PlayError):
    """Query has no results returned."""


class EmptyQueue(QueueError):
    """There is nothing in the queue."""


class InvalidPlaylist(QueueError):
    """The playlist is invalid."""
