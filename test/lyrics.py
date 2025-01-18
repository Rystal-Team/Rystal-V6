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
from deep_translator import GoogleTranslator
from langdetect import detect
import time

yt = YouTube("https://www.youtube.com/watch?v=impSuIygMiQ&ab_channel=THEFIRSTTAKE")
captions = yt.video.get_captions()
print(captions)

data = {}
base_transcript = []
lyrics = {}


if captions:
    for caption in captions:
        print(f'language: {caption.language}, language code: {caption.language_code}')
        print(caption.url)
        data[caption.language_code] = []
        for line in caption.transcript:
            data[caption.language_code].append(line)

        print(data[caption.language_code])
else:
    print("No captions available")
    exit()

detected_language = detect(yt.video.metadata['videoDetails']['title'])
print(f'detected as {detected_language}')

"""for line in data[detected_language]:
    base_transcript.append(line['text'])
print(base_transcript)"""

"""create_timer = time.time()
target = "zh-TW"

try:
    translation = GoogleTranslator(source=detected_language, target=target).translate_batch(base_transcript)
except KeyError:
    translation = GoogleTranslator(source=str(list(data.keys())[0]), target=target).translate_batch(base_transcript)

for index, line in enumerate(data[detected_language]):
    data[detected_language][index]['text'] = translation[index]
    lyrics = data[detected_language]

print(f'translated in {time.time() - create_timer} seconds')
"""