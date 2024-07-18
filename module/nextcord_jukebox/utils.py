

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

import random
import re
import string


async def generate_secret(length=16):
    """
    Generate a random secret string of a specified length.

    Args:
        length (int, optional): Length of the generated secret string (default is 16).

    Returns:
        str: Randomly generated secret string consisting of alphanumeric characters.

    """
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(length))


async def get_playlist_id(url):
    """
    Extracts the playlist ID from a YouTube playlist URL.

    Args:
        url (str): YouTube playlist URL.

    Returns:
        str: Playlist ID extracted from the URL, or None if no valid ID found.

    """
    return re.search(r"list=([a-zA-Z0-9_-]+)", url).group(1) if re.search(r"list=([a-zA-Z0-9_-]+)", url) else None


async def get_video_id(url):
    """
    Extracts the video ID from a YouTube video URL.

    Args:
        url (str): YouTube video URL.

    Returns:
        str: Video ID extracted from the URL, or None if no valid ID found.

    """
    return (match.group(1) if (match := re.search(
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)(["
        r"a-zA-Z0-9_-]{11})",
        url, )) else None)


def to_timestamp(dt):
    """
    Converts a datetime object to a Unix timestamp.

    Args:
        dt (datetime.datetime): A datetime object to convert to timestamp.

    Returns:
        int: Unix timestamp.
    """
    return int(dt.timestamp())
