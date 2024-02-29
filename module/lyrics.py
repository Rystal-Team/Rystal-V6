"""import os, json, nextcord
from lyricsgenius import Genius

genius = Genius(os.getenv("GENIUS_APIKEY"))


class Song(object):
    def __init__(self, title, lyrics, thumbnail, url):
        self._title = title
        self._lyrics = lyrics
        self._thumbnail = thumbnail
        self._url = url

    @property
    def title(self) -> str:
        return self._title

    @property
    def lyrics(self) -> str:
        return self._lyrics

    @property
    def thumbnail(self) -> str:
        return self._thumbnail

    @property
    def url(self) -> str:
        return self._url


class Searcher:
    @staticmethod
    async def search_song(term):
        return_dump = []
        result = genius.search_songs(term)

        for song in result["hits"]:
            if song["type"] == "song":
                song_object = Song(
                    song["result"]["title"],
                    genius.lyrics(song["result"]["id"]),
                    song["result"]["song_art_image_url"],
                    song["result"]["url"],
                )

                return_dump.append(song_object)

        return return_dump
"""