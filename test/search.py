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

import re

from termcolor import colored


class StringMatcher:
    def __init__(self, titles, debug=False):
        self.titles = titles
        self.debug = debug

    def lev_dist(self, s1, s2):
        if len(s1) < len(s2):
            return self.lev_dist(s2, s1)

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

    def calc_score(self, dist, max_len):
        return 1 - (dist / max_len)

    def split(self, text):
        return re.split(r"\s+|[^\w\s・]", text)

    def term_sim(self, q_term, t_term):
        max_len = max(len(q_term), len(t_term))
        dist = self.lev_dist(q_term, t_term)
        return self.calc_score(dist, max_len)

    def match(self, query, case_sens=True, threshold=0.8):
        if not case_sens:
            query = query.lower()

        q_terms = self.split(query)
        results = []

        for title in self.titles:
            t_proc = title.lower() if not case_sens else title
            t_terms = self.split(t_proc)

            if query in t_proc:
                results.append((title, 1.0))
                continue

            highest_score = 0
            for q_term in q_terms:
                for t_term in t_terms:
                    if q_term in t_term:
                        if q_term in t_term or t_term in q_term:
                            highest_score = max(highest_score, 0.9)
                        else:
                            sim_score = self.term_sim(q_term, t_term)
                            highest_score = max(highest_score, sim_score)
                        break

            if highest_score >= threshold:
                results.append((title, highest_score))
            else:
                if self.debug:
                    print(
                        colored(
                            f"Unmatch >  {title} (Score: {highest_score:.2f})", "grey"
                        )
                    )

        results.sort(key=lambda x: x[1], reverse=True)
        return results


titles = [
    "夕刻、夢ト見紛ウ / アステル・レダ × カグラナナ【 歌ってみた 】",
    "【歌ってみた】一度だけの恋なら【とこ尊楓リゼるる】",
    "仮死化 / 遼遼 (Covered by ゆめおいまちた)【歌ってみた/にじさんじ/夢追翔/町田ちま】",
]

matcher = StringMatcher(titles, debug=True)

queries = [
    "cover",
    "仮死化",
    "covered by 町田ちま",
    "夢追翔 and 町田ちま",
    "一度だけの恋なら とこ",
    "   一度だ  け  の   恋   なら",
    "カグラナナ",
    "アステル レダ",
]

for q in queries:
    print(f"Matches for '{q}':")
    matches = matcher.match(q, case_sens=False, threshold=0.8)
    for t, s in matches:
        print(colored(f"Match >  {t} (Score: {s:.2f})", "green"))
