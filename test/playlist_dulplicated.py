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

from meta_yt import YouTube
from pytube import Playlist

playlist = Playlist("https://www.youtube.com/playlist?list=PL1zOoe1s6s3wBi-q9U5iMwQ3BNqJKoR_y")
print(len(playlist))

unique = []
duplicate = []

for i, song in enumerate(playlist):
    yt = YouTube(song)
    if yt.video.title not in unique:
        unique.append(yt.video.title)
    else:
        print(f"Duplicate song found at index {i}")
        duplicate.append(yt.video.title)
    print(str(i + 1), yt.video.title)

print("Total duplicates found:", len(duplicate))
print(duplicate)
{"url": "https://youtu.be/hkBbUf4oGfA", "title": "\u83c5\u7530\u5c06\u6689 \u300e\u8679\u300f", "views": 158964981, "duration": 271, "thumbnail": "https://i.ytimg.com/vi/hkBbUf4oGfA/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLDL5OQbtnlGR--SBYxsKZQzGcQ-XQ", "channel": "\u83c5\u7530\u5c06\u6689 Official Channel", "channel_url": "https://www.youtube.com/channel/UCn2UPKO76hTLYEUVzVMBAeg", "thumbnails": [{"url": "https://i.ytimg.com/vi/hkBbUf4oGfA/default.jpg", "width": 120, "height": 90}, {"url": "https://i.ytimg.com/vi/hkBbUf4oGfA/mqdefault.jpg", "width": 320, "height": 180}, {"url": "https://i.ytimg.com/vi/hkBbUf4oGfA/hqdefault.jpg", "width": 480, "height": 360}, {"url": "https://i.ytimg.com/vi/hkBbUf4oGfA/sddefault.jpg", "width": 640, "height": 480}, {"url": "https://i.ytimg.com/vi/hkBbUf4oGfA/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLDL5OQbtnlGR--SBYxsKZQzGcQ-XQ", "width": 686, "height": 386}]}
