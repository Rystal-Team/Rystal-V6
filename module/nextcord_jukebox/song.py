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

from .timer import CountTimer


class Song:
    def __init__(
        self,
        url,
        title=None,
        views=None,
        duration=None,
        thumbnail=None,
        channel=None,
        channel_url=None,
    ):
        self.url = url
        self.title = title
        self.name = title
        self.views = views
        self.duration = duration
        self.thumbnail = thumbnail
        self.channel = channel
        self.channel_url = channel_url

        self.timer = CountTimer()
        self.source_url = None
        self.extracted_metadata = False  # attribute to track metadata extraction

    async def reset(self):
        self.timer.reset()

    async def resume(self):
        self.timer.resume()

    async def pause(self):
        self.timer.pause()

    async def start(self):
        self.timer.start()
