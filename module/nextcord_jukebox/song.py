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

from .timer import CountTimer


class Song:
    """
    A class to represent a song with various attributes and a timer.

    Attributes:
        url (str): The URL of the song.
        title (str, optional): The title of the song.
        views (int, optional): The number of views of the song.
        duration (int, optional): The duration of the song in seconds.
        thumbnail (str, optional): The URL of the song's thumbnail.
        channel (str, optional): The name of the channel that uploaded the song.
        channel_url (str, optional): The URL of the channel that uploaded the song.
        thumbnails (list, optional): A list of thumbnail URLs for the song.
        timer (CountTimer): An instance of CountTimer to track the song's playback time.
        source_url (str, optional): The source URL of the song.
        extracted_metadata (bool): A flag indicating whether metadata has been extracted.
    """

    def __init__(
        self,
        url,
        title=None,
        views=None,
        duration=None,
        thumbnail=None,
        channel=None,
        channel_url=None,
        thumbnails=None,
    ):
        """
        Initializes a Song instance with the given attributes.

        Args:
            url (str): The URL of the song.
            title (str, optional): The title of the song.
            views (int, optional): The number of views of the song.
            duration (int, optional): The duration of the song in seconds.
            thumbnail (str, optional): The URL of the song's thumbnail.
            channel (str, optional): The name of the channel that uploaded the song.
            channel_url (str, optional): The URL of the channel that uploaded the song.
            thumbnails (list, optional): A list of thumbnail URLs for the song.
        """
        self.url = url
        self.title = title
        self.name = title
        self.views = views
        self.duration = duration
        self.thumbnail = thumbnail
        self.channel = channel
        self.channel_url = channel_url
        self.thumbnails = thumbnails

        self.timer = CountTimer()
        self.source_url = None
        self.extracted_metadata = False

    async def reset(self):
        """
        Resets the song's timer.
        """
        self.timer.reset()

    async def resume(self):
        """
        Resumes the song's timer.
        """
        self.timer.resume()

    async def pause(self):
        """
        Pauses the song's timer.
        """
        self.timer.pause()

    async def start(self):
        """
        Starts the song's timer.
        """
        self.timer.start()
