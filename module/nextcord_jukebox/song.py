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

from typing import List, Optional

from .timer import CountTimer


class Song:
    """
    A class to represent a song with various attributes and a timer.

    Attributes:
        url (str): The URL of the song.
        title (Optional[str]): The title of the song.
        views (Optional[int]): The number of views of the song.
        duration (Optional[int]): The duration of the song in seconds.
        thumbnail (Optional[str]): The URL of the song's thumbnail.
        channel (Optional[str]): The name of the channel that uploaded the song.
        channel_url (Optional[str]): The URL of the channel that uploaded the song.
        thumbnails (Optional[List[str]]): A list of thumbnail URLs for the song.
        timer (CountTimer): An instance of CountTimer to track the song's playback time.
        source_url (Optional[str]): The source URL of the song.
        extracted_metadata (bool): A flag indicating whether metadata has been extracted.
    """

    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        views: Optional[int] = None,
        duration: Optional[int] = None,
        thumbnail: Optional[str] = None,
        channel: Optional[str] = None,
        channel_url: Optional[str] = None,
        thumbnails: Optional[List[str]] = None,
    ) -> None:
        """
        Initializes a Song instance with the given attributes.

        Args:
            url (str): The URL of the song.
            title (Optional[str]): The title of the song.
            views (Optional[int]): The number of views of the song.
            duration (Optional[int]): The duration of the song in seconds.
            thumbnail (Optional[str]): The URL of the song's thumbnail.
            channel (Optional[str]): The name of the channel that uploaded the song.
            channel_url (Optional[str]): The URL of the channel that uploaded the song.
            thumbnails (Optional[List[str]]): A list of thumbnail URLs for the song.
        """
        self.url: str = url
        self.title: Optional[str] = title or "Unknown"
        self.name: Optional[str] = title or "Unknown"
        self.views: Optional[int] = views or 0
        self.duration: Optional[int] = duration or 1
        self.thumbnail: Optional[str] = thumbnail or ""
        self.channel: Optional[str] = channel or "Unknown"
        self.channel_url: Optional[str] = channel_url or ""
        self.thumbnails: Optional[List[str]] = thumbnails or []

        if self.duration < 1:
            self.duration = 1

        self.timer: CountTimer = CountTimer()
        self.source_url: Optional[str] = None
        self.extracted_metadata: bool = False

    async def reset(self) -> None:
        """Resets the song's timer."""
        self.timer.reset()

    async def resume(self) -> None:
        """Resumes the song's timer."""
        self.timer.resume()

    async def pause(self) -> None:
        """Pauses the song's timer."""
        self.timer.pause()

    async def start(self) -> None:
        """Starts the song's timer."""
        self.timer.start()
