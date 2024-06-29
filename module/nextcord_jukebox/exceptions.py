"""
Custom exceptions for the Nextcord Jukebox application.

These exceptions are used to handle various error scenarios that can occur in the Nextcord Jukebox, providing meaningful error messages and descriptions.

Classes:
    NextcordJukeBoxError(Exception): Base class for all Nextcord Jukebox exceptions.
    QueueError(NextcordJukeBoxError): Exception raised for queue-related errors.
    PlayError(NextcordJukeBoxError): Exception raised for play-related errors.
    FailedConnection(NextcordJukeBoxError): Exception raised when the bot fails to connect to a voice channel.
    UserNotConnected(PlayError): Exception raised when the user is not connected to a voice channel.
    VoiceChannelMismatch(PlayError): Exception raised when the user is connected to a different voice channel than the bot.
    NotConnected(PlayError): Exception raised when the bot is not connected to a voice channel.
    LoadingStream(PlayError): Exception raised when the player is already loading a stream.
    NotPlaying(PlayError): Exception raised when the bot is not playing music.
    NothingPlaying(PlayError): Exception raised when there is nothing currently playing.
    AlreadyPaused(PlayError): Exception raised when the music is already paused.
    NotPaused(PlayError): Exception raised when the music is not paused.
    NoQueryResult(PlayError): Exception raised when a query returns no results.
    EmptyQueue(QueueError): Exception raised when there is nothing in the queue.
"""


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
