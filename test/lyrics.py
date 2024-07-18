#    ------------------------------------------------------------
#    Copyright (c) 2024 Rystal-Team
#  #
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#  #
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#  #
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.
#    ------------------------------------------------------------
#  #

import json
import os

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
    async def search_song(term):
        return_dump = []
        result = genius.search_songs(term)

        with open(".json", "w") as f:
            json.dump(result, f)

        for song in result["hits"]:
            print(song)
            if song["type"] == "song":
                song_object = Song(
                    song["result"]["title"],
                    genius.lyrics(song["result"]["id"]),
                    song["result"]["song_art_image_url"],
                    song["result"]["url"],
                )

                return_dump.append(song_object)

        return return_dump
