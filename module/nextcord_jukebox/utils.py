
import re
import string
import random


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
    return (re.search(r"list=([a-zA-Z0-9_-]+)", url).group(1)if re.search(r"list=([a-zA-Z0-9_-]+)", url)else None)


async def get_video_id(url):
    """
    Extracts the video ID from a YouTube video URL.

    Args:
        url (str): YouTube video URL.

    Returns:
        str: Video ID extracted from the URL, or None if no valid ID found.

    """
    return (match.group(1)if (match := re.search(r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})", url,))else None)
