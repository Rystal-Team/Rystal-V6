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

import re

from termcolor import colored


class SongMatcher:
    """A class for matching songs based on a query string."""

    @classmethod
    def lev_dist(cls, s1, s2):
        """
        Computes the Levenshtein distance between two strings.

        Args:
            s1 (str): The first string.
            s2 (str): The second string.

        Returns:
            int: The Levenshtein distance between the two strings.
        """
        if len(s1) < len(s2):
            return cls.lev_dist(s2, s1)

        if len(s2) == 0:
            return len(s1)

        prev = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                ins = prev[j + 1] + 1
                dels = curr[j] + 1
                subs = prev[j] + (c1 != c2)
                curr.append(min(ins, dels, subs))
            prev = curr

        return prev[-1]

    @classmethod
    def calc_score(cls, dist, max_len):
        """
        Calculates a similarity score based on the Levenshtein distance.

        Args:
            dist (int): The Levenshtein distance.
            max_len (int): The maximum length of the two strings compared.

        Returns:
            float: The similarity score (between 0 and 1).
        """
        return 1 - (dist / max_len)

    @classmethod
    def split(cls, text):
        """
        Splits a text string into terms based on whitespace and non-word characters.

        Args:
            text (str): The text string to split.

        Returns:
            list of str: A list of terms.
        """
        return re.split(r"\s+|[^\w\s・]", text)

    @classmethod
    def term_sim(cls, q_term, t_term):
        """
        Computes the similarity score between two terms.

        Args:
            q_term (str): The query term.
            t_term (str): The target term.

        Returns:
            float: The similarity score (between 0 and 1).
        """
        max_len = max(len(q_term), len(t_term))
        dist = cls.lev_dist(q_term, t_term)
        return cls.calc_score(dist, max_len)

    @classmethod
    def match(cls, song_queue, query, case_sens=True, threshold=0.8, debug=False):
        """
        Matches songs from the song queue based on the query string.

        Args:
            song_queue (list of Song): The list of songs to search.
            query (str): The query string.
            case_sens (bool): Whether the match should be case-sensitive.
            threshold (float): The minimum similarity score to consider a match.
            debug (bool): Whether to print debug information.

        Returns:
            list of tuple: A list of tuples containing matched songs and their scores.
        """
        highest_score = 0
        if not case_sens:
            query = query.lower()

        query = re.sub(r"[^\w\s]", "", query)
        q_terms = cls.split(query)
        results = []

        for song in song_queue:
            song_title = re.sub(r"[^\w\s]", "", song.name)
            song_channel = song.channel

            title_proc = song_title.lower() if not case_sens else song_title
            channel_proc = song_channel.lower() if not case_sens else song_channel

            t_terms = cls.split(title_proc)
            c_terms = cls.split(channel_proc)

            combined_terms = t_terms + c_terms

            match_found = False
            for q_term in q_terms:
                highest_score = 0

                if q_term in title_proc or q_term in channel_proc:
                    highest_score = 1
                    match_found = True
                    break

                for t_term in combined_terms:
                    sim_score = cls.term_sim(q_term, t_term)
                    highest_score = max(highest_score, sim_score)

                if highest_score >= threshold:
                    match_found = True
                    break

            if match_found:
                results.append((song, highest_score))
            else:
                if debug:
                    print(
                        colored(
                            f"Unmatch >  {song_title} by {song_channel} (Score: {highest_score:.2f})",
                            "grey",
                        )
                    )

        results.sort(key=lambda x: x[1], reverse=True)
        return results


class Song:
    """
    A class representing a song with a name and a channel.

    Attributes:
        name (str): The name of the song.
        channel (str): The channel of the song.
    """

    def __init__(self, name, channel):
        self.name = name
        self.channel = channel


if __name__ == "__main__":
    songs = [
        Song(
            name="夕刻、夢ト見紛ウ / アステル・レダ × カグラナナ【 歌ってみた 】",
            channel="カグラナナ",
        ),
        Song(
            name="【歌ってみた】一度だけの恋なら【とこ尊楓リゼるる】",
            channel="戌亥とこ",
        ),
        Song(
            name="仮死化 / 遼遼 (Covered by ゆめおいまちた)【歌ってみた/にじさんじ/夢追翔/町田ちま】",
            channel="夢追翔のJUKEBOX",
        ),
        Song(name="[MV] We don't talk anymore", channel="Justin Bieber"),
        Song(
            name="【歌衣メイカ爆誕祭2024】W/X/Y／歌衣メイカ × アステル・レダ",
            channel="歌衣メイカ",
        ),
    ]

    queries = [
        "cover",
        "仮死化",
        "covered by 町田ちま",
        "夢追翔 and 町田ちま",
        "一度だけの恋なら とこ",
        "   一度だ  け  の   恋   なら",
        "カグラナナ",
        "アステル レダ",
        "アステルレダ",
        "w/x/y",
    ]

    for q in queries:
        print(f"Matches for '{q}':")
        matches = SongMatcher.match(
            songs, q, case_sens=False, threshold=0.8, debug=True
        )
        for t, s in matches:
            print(colored(f"Match >  {t.name} (Score: {s:.2f})", "green"))
