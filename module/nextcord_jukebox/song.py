"""
The Song class represents a song with various metadata and provides methods to manage its playback timer.

Attributes:
    url (str): The URL of the song.
    title (str): The title of the song.
    views (int): The number of views the song has.
    duration (int): The duration of the song in seconds.
    thumbnail (str): The URL of the song's thumbnail image.
    channel (str): The name of the channel that uploaded the song.
    channel_url (str): The URL of the channel that uploaded the song.
    video (Any): The video object associated with the song.
    timer (CountTimer): An instance of CountTimer to manage the playback time.
    source_url (str, optional): The source URL of the song. Default is None.

Methods:
    reset():
        Resets the playback timer for the song.

    resume():
        Resumes the playback timer for the song.

    pause():
        Pauses the playback timer for the song.

    start():
        Starts the playback timer for the song.
"""

from module.timer import CountTimer


class Song(object):
    def __init__(
        self,
        url,
        title,
        views,
        duration,
        thumbnail,
        channel,
        channel_url,
        video,
    ) -> None:
        """
        Initializes a Song instance with the provided metadata.

        Args:
            url (str): The URL of the song.
            title (str): The title of the song.
            views (int): The number of views the song has.
            duration (int): The duration of the song in seconds.
            thumbnail (str): The URL of the song's thumbnail image.
            channel (str): The name of the channel that uploaded the song.
            channel_url (str): The URL of the channel that uploaded the song.
            video (Any): The video object associated with the song.
        """
        self.url = url
        self.title = title
        self.views = views
        self.name = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.channel = channel
        self.channel_url = channel_url
        self.video = video

        self.timer = CountTimer()
        self.source_url = None

    async def reset(self):
        """
        Resets the playback timer for the song.
        """
        self.timer.reset()

    async def resume(self):
        """
        Resumes the playback timer for the song.
        """
        self.timer.resume()

    async def pause(self):
        """
        Pauses the playback timer for the song.
        """
        self.timer.pause()

    async def start(self):
        """
        Starts the playback timer for the song.
        """
        self.timer.start()
