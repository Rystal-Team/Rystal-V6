class NextcordJukeBoxError(Exception):
    """Base Nextcord Jukebox Exception."""

    pass


class QueueError(NextcordJukeBoxError):
    """Queue related function error."""

    pass


class PlayError(NextcordJukeBoxError):
    """Play related function errored."""

    pass


class FailedConnection(NextcordJukeBoxError):
    """Failed to connect to a voice channel."""

    pass


class UserNotConnected(PlayError):
    """The user is not connected to a voice channel."""

    pass


class VoiceChannelMismatch(PlayError):
    """The user is connected to a different voice channel as the bot."""

    pass


class NotConnected(PlayError):
    """The bot is not connected to a voice channel."""

    pass


class LoadingStream(PlayError):
    """The player is loading stream already, please slow down."""

    pass


class NotPlaying(PlayError):
    """Not playing music."""

    pass


class NothingPlaying(PlayError):
    """Nothing is playing."""

    pass


class AlreadyPaused(PlayError):
    """The music is already paused."""

    pass


class NotPaused(PlayError):
    """The music is not paused."""

    pass


class NoQueryResult(PlayError):
    """Query has no results returned."""

    pass


class EmptyQueue(QueueError):
    """There is nothing in the queue."""

    pass


class InvalidPlaylist(QueueError):
    """The playlist is invalid."""

    pass
