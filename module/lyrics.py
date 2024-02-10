import os
from lyricsgenius import Genius
from lyricsgenius.genius import Artist as GeniusArtist

genius = Genius(os.getenv("GENIUS_APIKEY"))


class SongLyrics(object):
    def __init__(self, lyrics: str):
        self.lyrics = lyrics

    @property
    def word_count(self) -> int:
        return len(self.lyrics.split())


class Artist:
    def __init__(self):
        self._artist = None

    async def get_artist(self, artist_name: str) -> GeniusArtist:
        artist = genius.search_artist(artist_name, max_songs=10, sort="popularity")

        self.artist = artist
        return artist

    async def get_lyrics(self, song_name) -> SongLyrics:
        song = genius.search_song(song_name, self.artist)

        try:
            lyrics = SongLyrics(lyrics=song.lyrics)
            return lyrics
        except Exception:
            return None

    @property
    def artist(self) -> GeniusArtist:
        return self._artist
