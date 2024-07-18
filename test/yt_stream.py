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

import time

import pytube
import yt_dlp
from termcolor import colored

print(colored(text="(FROM URL)", color="dark_grey"))
timer = time.time()

ydl = yt_dlp.YoutubeDL(
    {
        "format"        : "bestaudio/best",
        "noplaylist"    : True,
        "ignoreerrors"  : True,
        "quiet"         : True,
        "no_warnings"   : True,
        "source_address": "0.0.0.0",
        "forceip"       : "4",
        "skip_download" : True,
        "extract_flat"  : True,
        "default_search": "auto",
    }
)

yt = pytube.YouTube("https://www.youtube.com/watch?v=hTqFFYX93yY")
print(yt.title)
print(yt.views)
print(yt.length)
print(yt.thumbnail_url)
print(colored(text=f"Time taken: {time.time() - timer}", color="dark_grey"))

print(colored(text="(FROM URL)", color="dark_grey"))
timer = time.time()

data = ydl.extract_info(
    "https://www.youtube.com/watch?v=hTqFFYX93yY",
    download=False,
)

print(data["title"])
print(data["view_count"])
print(data["duration"])
print(data["thumbnail"])
print(data["uploader"])
print(data["uploader_url"])
print(data["url"])
print(colored(text=f"Time taken: {time.time() - timer}", color="dark_grey"))
