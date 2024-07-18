

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

from io import BytesIO
from typing import List, Optional

import requests
from PIL import Image, ImageDraw, ImageFont


def create_top_songs_poster(songs: List[dict], title: str, description: str,
                            detail_texts: Optional[List[str]] = None) -> Image:
    """
    Create a poster for top songs with given title, description, and optional details.

    Args:
        songs (List[dict]): A list of dictionaries, each containing 'title', 'artist', 'replays', and 'thumbnail' keys.
        title (str): The title of the poster.
        description (str): The description text on the poster.
        detail_texts (Optional[List[str]]): A list of additional detail texts to be displayed on the poster.

    Returns:
        Image: The generated poster as a PIL Image object.
    """

    def draw_rounded_text(text_str: str, font: ImageFont.FreeTypeFont, x_pad: int, y_pad: int, radius: int, pos: tuple,
                          color: str = "#97A8CB") -> int:
        width, height = draw.textbbox((0, 0), text_str, font=font)[2:4]
        rect_w, rect_h = width + 2 * x_pad, 24 + 2 * y_pad
        x, y = pos
        rect_bbox = (x, y, x + rect_w, y + rect_h)
        draw.rounded_rectangle(rect_bbox, radius=radius, fill="#1c1f26")
        draw.text((x + x_pad, y + y_pad - 4), text_str, font=font, fill=color)
        return rect_w

    def format_number(num: float) -> str:
        if num < 1000:
            return str(num)
        for unit in ['', 'k', 'M', 'B', 'T']:
            if abs(num) < 1000.0:
                return f"{num:3.1f}{unit}"
            num /= 1000.0

    def truncate_text(text_str: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
        width, _ = draw.textbbox((0, 0), text_str, font=font)[2:4]
        if width <= max_w:
            return text_str
        while width > max_w:
            text_str = text_str[:-1]
            width, _ = draw.textbbox((0, 0), text_str + "...", font=font)[2:4]
        return text_str + "..."

    def load_image_from_url(url: str) -> Image:
        return Image.open(BytesIO(requests.get(url).content)).convert("RGBA")

    canvas = Image.new('RGB', (800, 1300), color="#16181d")
    draw = ImageDraw.Draw(canvas)

    fonts = {name: ImageFont.truetype(f"../font/GoNotoKurrent-{style}.ttf", size) for name, style, size in [
        ("title", "Bold", 36), ("description", "Regular", 28), ("index", "Regular", 20),
        ("song", "Regular", 28), ("artist", "Regular", 15), ("replay", "Bold", 25), ("details", "Regular", 24)
    ]}

    for path, pos, size in [
        ("../assets/logo.png", (60, 90), (100, 100)),
        ("../assets/get-it-on-github.png", (292, 1160), (215, 83))
    ]:
        canvas.paste(Image.open(path).resize(size), pos, Image.open(path).resize(size))

    draw.text((170, 95), title, font=fonts["title"], fill="#ffffff")
    draw.text((170, 140), description, font=fonts["description"], fill="#ffffff")
    draw.line((50, 250, 750, 250), fill="#1c1f26", width=3)

    details_x = 55
    for text in detail_texts or []:
        details_x += draw_rounded_text(text, fonts["details"], 15, 4, 15, (details_x, 205)) + 10

    for i, song in enumerate(songs):
        y_pos = 260 + i * 90
        song_text = truncate_text(song['title'], fonts["song"], 540)
        artist_text = truncate_text(f"{song['artist']}", fonts["artist"], 540)
        replay_text = format_number(song['replays'])

        draw.text((50, y_pos + 22), str(i + 1), font=fonts["index"], fill="#576175")
        thumbnail = load_image_from_url(song['thumbnail']).resize((106, 60)).crop((23, 0, 83, 60))
        canvas.paste(thumbnail, (80, y_pos + 8), thumbnail)
        draw.text((150, y_pos + 5), song_text, font=fonts["song"], fill="#ffffff")
        draw.text((150, y_pos + 40), artist_text, font=fonts["artist"], fill="#97A8CB")
        draw.text((750, y_pos + 30), replay_text, font=fonts["replay"], fill="#ffffff", anchor="rm")

        if i < len(songs) - 1:
            draw.line((50, y_pos + 80, 750, y_pos + 80), fill="#1c1f26", width=2)

    draw.rectangle((750, 0, 800, 250), fill="#16181d")

    canvas.show()
    return canvas


songs = [
    {"title"    : "雨に消えて", "artist": "Astel Leda - Topic", "replays": 102,
     "thumbnail": "https://images-ext-1.discordapp.net/external/yWjDH2XP1qCsNXVPBBuRP1QgqnsGlgtFg8yDtO9iy54/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLA2djoh4vlCPhkfaKxoAWmVnCpqmg/https/i.ytimg.com/vi/1u8om8Vj_QI/hq720.jpg?format=webp&width=574&height=323"},
    {"title"    : " 夕刻、夢ト見紛ウ / アステル・レダ × カグラナナ【 歌ってみた 】",
     "artist"   : "カグラナナchannel／ななかぐら", "replays": 95,
     "thumbnail": "https://images-ext-1.discordapp.net/external/MGBcbzbpJ7iw2wU0SnMRHE6D1R6O5Murgdtar3kfAXQ/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLApETuGaqP45CSwnEelrT0dvMFYtA/https/i.ytimg.com/vi/AEGJSVH-y28/hq720.jpg?format=webp&width=574&height=323"},
    {"title"    : "星街すいせい - Stellar Stellar / THE FIRST TAKE", "artist": "THE FIRST TAKE", "replays": 92,
     "thumbnail": "https://images-ext-1.discordapp.net/external/kkgoJVji0x_eeqKzbArDa1hxip8JHdrbZqSFO7gxyko/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBUg4Sijlk0IgDoVtDCWtTa2I1bQw/https/i.ytimg.com/vi/AAsRtnbDs-0/hq720.jpg?format=webp&width=574&height=323"},
    {"title"    : "Official髭男dism - Cry Baby［Official Live Video］", "artist": "Official髭男dism", "replays": 86,
     "thumbnail": "https://images-ext-1.discordapp.net/external/Da7gdfzhCwqmn_3iDUCbza16ZMX6VEaA7OQB-YtMoPg/https/i.ytimg.com/vi/V8kXFEWNTYc/sddefault.jpg?format=webp&width=536&height=402"},
    {"title"    : "【歌わせていただきました】星が瞬くこんな夜に/Supercell【英リサ】", "artist": "英リサ.Hanabusa Lisa",
     "replays"  : 78,
     "thumbnail": "https://images-ext-1.discordapp.net/external/n8rD6wjTv7VsMiJdKUTpeK29QC6V16-UK0T_q7I99Mk/%3Fsqp%3D-oaymwE7CK4FEIIDSFryq4qpAy0IARUAAAAAGAElAADIQj0AgKJD8AEB-AH-CYAC0AWKAgwIABABGEUgUChlMA8%3D%26rs%3DAOn4CLAlMZEwGOalblYyacfxxq7Ozzpj8Q/https/i.ytimg.com/vi/nl12QpTMNLg/hq720.jpg?format=webp&width=574&height=323"},
    {"title"    : "【MV】女の子になりたい／まふまふ", "artist": "まふまふちゃんねる", "replays": 70,
     "thumbnail": "https://images-ext-1.discordapp.net/external/p98TFofizNbKwZF9mOecEste-i2wku1jjznWliIYNas/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBO5QBGCjs41Xwzj8bRX84jCucTgg/https/i.ytimg.com/vi/ucbx9we6EHk/hq720.jpg?format=webp&width=574&height=323"},
    {"title"    : "シネマ / 星街すいせい×奏手イヅル×アステル･レダ(Cover)", "artist": "Suisei Channel", "replays": 63,
     "thumbnail": "https://images-ext-1.discordapp.net/external/9FN1F9SEVpEUwsC0hiEIIeiLntoGXiTci34LwAa-YzI/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBKBwMaD0K3BGQs6iZh5M3dtjX_EQ/https/i.ytimg.com/vi/UXQDUhSr8nU/hq720.jpg?format=webp&width=574&height=323"},
    {"title"    : "仮死化 / 遼遼 (Covered by ゆめおいまちた)【歌ってみた/にじさんじ/夢追翔/町田ちま】",
     "artist"   : "夢追翔のJUKE BOX", "replays": 59,
     "thumbnail": "https://i.ytimg.com/vi/Mj38FoEYVGA/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLBSIu-0dRpkSW21mPZVbQQtwCmugw"},
    {"title"    : "【歌ってみた】一度だけの恋なら【とこ尊楓リゼるる】", "artist": "戌亥とこ -Inui Toko-", "replays": 52,
     "thumbnail": "https://images-ext-1.discordapp.net/external/PQh59mre1DHlkx1AJRgI_mEbf4xD3qfmw3vq5R8D6vo/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBplO6VYWV7hhA-xhX7YPp43Lh_aw/https/i.ytimg.com/vi/zokUrGt0iuc/hq720.jpg?format=webp&width=574&height=323"},
    {
        "title"    : "七海うらら『Øver Rider』MV(スマホゲーム『BLACK STELLA PTOLOMEA』主題歌)",
        "artist"   : "七海うらら*歌channel", "replays": 42,
        "thumbnail": "https://images-ext-1.discordapp.net/external/Y5O-1pCz1-tsnUi0Ez-dD-mnCRF4WtdoG-WtL0hcXyw/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLAaicehaeyx9U3kFvuas_1cJlDOXA/https/i.ytimg.com/vi/8M3geFKQ-hU/hq720.jpg?format=webp&width=574&height=323"
    }
]

title = "リスタルミュージック"
description = "本月最も再生された曲"
create_top_songs_poster(songs, title, description,
                        detail_texts=["41時間+", "1871曲再生しました", "18% アステル・レダ"])
print("Created poster")
