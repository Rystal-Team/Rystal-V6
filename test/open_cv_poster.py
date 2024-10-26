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

import time
from io import BytesIO
from typing import List, Optional

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont


def create_top_songs_poster(
    songs: List[dict],
    title: str,
    description: str,
    detail_texts: Optional[List[str]] = None,
) -> np.ndarray:
    def draw_text(img, text, position, font_path, font_size, color, center=False):
        font = ImageFont.truetype(font_path, font_size)
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        text_size = draw.textbbox((0, 0), text, font=font)[2:4]
        if center:
            position = (
                position[0] - text_size[0] // 2,
                position[1] - text_size[1] // 2,
            )
        draw.text(position, text, font=font, fill=color)
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR), text_size

    def draw_rounded_rectangle(image, top_left, bottom_right, color, corner_radius):
        overlay = image.copy()
        corner_radius = min(
            corner_radius,
            (bottom_right[0] - top_left[0]) // 2,
            (bottom_right[1] - top_left[1]) // 2,
        )
        cv2.ellipse(
            overlay,
            (top_left[0] + corner_radius, top_left[1] + corner_radius),
            (corner_radius, corner_radius),
            180,
            0,
            90,
            color,
            -1,
        )
        cv2.ellipse(
            overlay,
            (bottom_right[0] - corner_radius, top_left[1] + corner_radius),
            (corner_radius, corner_radius),
            270,
            0,
            90,
            color,
            -1,
        )
        cv2.ellipse(
            overlay,
            (bottom_right[0] - corner_radius, bottom_right[1] - corner_radius),
            (corner_radius, corner_radius),
            0,
            0,
            90,
            color,
            -1,
        )
        cv2.ellipse(
            overlay,
            (top_left[0] + corner_radius, bottom_right[1] - corner_radius),
            (corner_radius, corner_radius),
            90,
            0,
            90,
            color,
            -1,
        )
        cv2.rectangle(
            overlay,
            (top_left[0] + corner_radius, top_left[1]),
            (bottom_right[0] - corner_radius, bottom_right[1]),
            color,
            -1,
        )
        cv2.rectangle(
            overlay,
            (top_left[0], top_left[1] + corner_radius),
            (bottom_right[0], bottom_right[1] - corner_radius),
            color,
            -1,
        )
        cv2.rectangle(
            overlay,
            (top_left[0] + corner_radius, top_left[1] + corner_radius),
            (bottom_right[0] - corner_radius, bottom_right[1] - corner_radius),
            color,
            -1,
        )
        return overlay

    def format_number(num: float) -> str:
        if num < 1000:
            return str(num)
        for unit in ["", "k", "M", "B", "T"]:
            if abs(num) < 1000.0:
                return f"{num:3.1f}{unit}"
            num /= 1000.0

    def truncate_text(text_str: str, font_path, font_size, max_w) -> str:
        font = ImageFont.truetype(font_path, font_size)
        width, _ = ImageDraw.Draw(Image.new("RGB", (0, 0))).textbbox(
            (0, 0), text_str, font=font
        )[2:4]
        if width <= max_w:
            return text_str
        while width > max_w:
            text_str = text_str[:-1]
            width, _ = ImageDraw.Draw(Image.new("RGB", (0, 0))).textbbox(
                (0, 0), text_str + "...", font=font
            )[2:4]
        return text_str + "..."

    def load_image_from_url(url: str) -> np.ndarray:
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            image = Image.open(BytesIO(resp.content)).convert("RGBA")
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)
        except (requests.RequestException, IOError):
            return np.zeros((200, 200, 4), dtype=np.uint8)

    def paste_image(background, overlay, x, y):
        y1, y2 = y, y + overlay.shape[0]
        x1, x2 = x, x + overlay.shape[1]
        alpha_s = overlay[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(0, 3):
            background[y1:y2, x1:x2, c] = (
                alpha_s * overlay[:, :, c] + alpha_l * background[y1:y2, x1:x2, c]
            )
        return background

    canvas = np.zeros((1300, 800, 3), dtype=np.uint8)
    canvas[:] = (29, 24, 22)

    font_paths = {
        "title"      : "../font/GoNotoKurrent-Bold.ttf",
        "description": "../font/GoNotoKurrent-Regular.ttf",
        "index"      : "../font/GoNotoKurrent-Regular.ttf",
        "song"       : "../font/GoNotoKurrent-Regular.ttf",
        "artist"     : "../font/GoNotoKurrent-Regular.ttf",
        "replay"     : "../font/GoNotoKurrent-Bold.ttf",
        "details"    : "../font/GoNotoKurrent-Regular.ttf",
    }

    logo = cv2.imread("../assets/logo.png", cv2.IMREAD_UNCHANGED)
    github_logo = cv2.imread("../assets/get-it-on-github.png", cv2.IMREAD_UNCHANGED)

    canvas = paste_image(canvas, cv2.resize(logo, (100, 100)), 60, 90)
    canvas = paste_image(canvas, cv2.resize(github_logo, (215, 83)), 292, 1160)

    canvas, _ = draw_text(
        canvas, title, (170, 95), font_paths["title"], 36, (255, 255, 255)
    )
    canvas, _ = draw_text(
        canvas, description, (170, 140), font_paths["description"], 28, (255, 255, 255)
    )
    cv2.line(canvas, (50, 250), (750, 250), (38, 31, 28), 3)

    details_x = 55
    for text in detail_texts or []:
        _, text_size = draw_text(
            canvas,
            text,
            (details_x + 15, 205),
            font_paths["details"],
            24,
            (151, 168, 203),
        )
        canvas = draw_rounded_rectangle(
            canvas,
            (details_x, 205),
            (details_x + text_size[0] + 25, 239),
            (38, 31, 28),
            15,
        )
        canvas, _ = draw_text(
            canvas,
            text,
            (details_x + 15, 205),
            font_paths["details"],
            24,
            (151, 168, 203),
        )
        details_x += text_size[0] + 40

    for i, song in enumerate(songs):
        y_pos = 260 + i * 90
        song_text = truncate_text(song["title"], font_paths["song"], 28, 540)
        artist_text = truncate_text(song["artist"], font_paths["artist"], 15, 540)
        replay_text = (
            format_number(song["replays"])
            if isinstance(song["replays"], int)
            else song["replays"]
        )

        canvas, _ = draw_text(
            canvas, str(i + 1), (50, y_pos + 22), font_paths["index"], 20, (87, 97, 117)
        )
        thumbnail = cv2.resize(
            load_image_from_url(song["thumbnail"]),
            (106, 60),
            interpolation=cv2.INTER_AREA,
        )
        canvas = paste_image(canvas, thumbnail[:, 23:83], 80, y_pos + 8)

        canvas, _ = draw_text(
            canvas, song_text, (150, y_pos + 5), font_paths["song"], 28, (255, 255, 255)
        )
        canvas, _ = draw_text(
            canvas,
            artist_text,
            (150, y_pos + 40),
            font_paths["artist"],
            15,
            (151, 168, 203),
        )
        canvas, _ = draw_text(
            canvas,
            replay_text,
            (750, y_pos + 30),
            font_paths["replay"],
            25,
            (255, 255, 255),
            center=True,
        )

        if i < len(songs) - 1:
            cv2.line(canvas, (50, y_pos + 80), (750, y_pos + 80), (38, 31, 28), 2)

    cv2.rectangle(canvas, (750, 0), (800, 250), (29, 24, 22), -1)

    return canvas


songs = [
    {
        "title"    : "雨に消えて",
        "artist"   : "Astel Leda - Topic",
        "replays"  : 102,
        "thumbnail": "https://images-ext-1.discordapp.net/external/yWjDH2XP1qCsNXVPBBuRP1QgqnsGlgtFg8yDtO9iy54/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLA2djoh4vlCPhkfaKxoAWmVnCpqmg/https/i.ytimg.com/vi/1u8om8Vj_QI/hq720.jpg?format=webp&width=574&height=323",
    },
    {
        "title"    : " 夕刻、夢ト見紛ウ / アステル・レダ × カグラナナ【 歌ってみた 】",
        "artist"   : "カグラナナchannel／ななかぐら",
        "replays"  : 95,
        "thumbnail": "https://images-ext-1.discordapp.net/external/MGBcbzbpJ7iw2wU0SnMRHE6D1R6O5Murgdtar3kfAXQ/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLApETuGaqP45CSwnEelrT0dvMFYtA/https/i.ytimg.com/vi/AEGJSVH-y28/hq720.jpg?format=webp&width=574&height=323",
    },
    {
        "title"    : "星街すいせい - Stellar Stellar / THE FIRST TAKE",
        "artist"   : "THE FIRST TAKE",
        "replays"  : 92,
        "thumbnail": "https://images-ext-1.discordapp.net/external/kkgoJVji0x_eeqKzbArDa1hxip8JHdrbZqSFO7gxyko/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBUg4Sijlk0IgDoVtDCWtTa2I1bQw/https/i.ytimg.com/vi/AAsRtnbDs-0/hq720.jpg?format=webp&width=574&height=323",
    },
    {
        "title"    : "Official髭男dism - Cry Baby［Official Live Video］",
        "artist"   : "Official髭男dism",
        "replays"  : 86,
        "thumbnail": "https://images-ext-1.discordapp.net/external/Da7gdfzhCwqmn_3iDUCbza16ZMX6VEaA7OQB-YtMoPg/https/i.ytimg.com/vi/V8kXFEWNTYc/sddefault.jpg?format=webp&width=536&height=402",
    },
    {
        "title"    : "【歌わせていただきました】星が瞬くこんな夜に/Supercell【英リサ】",
        "artist"   : "英リサ.Hanabusa Lisa",
        "replays"  : 78,
        "thumbnail": "https://images-ext-1.discordapp.net/external/n8rD6wjTv7VsMiJdKUTpeK29QC6V16-UK0T_q7I99Mk/%3Fsqp%3D-oaymwE7CK4FEIIDSFryq4qpAy0IARUAAAAAGAElAADIQj0AgKJD8AEB-AH-CYAC0AWKAgwIABABGEUgUChlMA8%3D%26rs%3DAOn4CLAlMZEwGOalblYyacfxxq7Ozzpj8Q/https/i.ytimg.com/vi/nl12QpTMNLg/hq720.jpg?format=webp&width=574&height=323",
    },
    {
        "title"    : "【MV】女の子になりたい／まふまふ",
        "artist"   : "まふまふちゃんねる",
        "replays"  : 70,
        "thumbnail": "https://images-ext-1.discordapp.net/external/p98TFofizNbKwZF9mOecEste-i2wku1jjznWliIYNas/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBO5QBGCjs41Xwzj8bRX84jCucTgg/https/i.ytimg.com/vi/ucbx9we6EHk/hq720.jpg?format=webp&width=574&height=323",
    },
    {
        "title"    : "シネマ / 星街すいせい×奏手イヅル×アステル･レダ(Cover)",
        "artist"   : "Suisei Channel",
        "replays"  : 63,
        "thumbnail": "https://images-ext-1.discordapp.net/external/9FN1F9SEVpEUwsC0hiEIIeiLntoGXiTci34LwAa-YzI/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBKBwMaD0K3BGQs6iZh5M3dtjX_EQ/https/i.ytimg.com/vi/UXQDUhSr8nU/hq720.jpg?format=webp&width=574&height=323",
    },
    {
        "title"    : "仮死化 / 遼遼 (Covered by ゆめおいまちた)【歌ってみた/にじさんじ/夢追翔/町田ちま】",
        "artist"   : "夢追翔のJUKE BOX",
        "replays"  : 59,
        "thumbnail": "https://i.ytimg.com/vi/Mj38FoEYVGA/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLBSIu-0dRpkSW21mPZVbQQtwCmugw",
    },
    {
        "title"    : "【歌ってみた】一度だけの恋なら【とこ尊楓リゼるる】",
        "artist"   : "戌亥とこ -Inui Toko-",
        "replays"  : 52,
        "thumbnail": "https://images-ext-1.discordapp.net/external/PQh59mre1DHlkx1AJRgI_mEbf4xD3qfmw3vq5R8D6vo/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLBplO6VYWV7hhA-xhX7YPp43Lh_aw/https/i.ytimg.com/vi/zokUrGt0iuc/hq720.jpg?format=webp&width=574&height=323",
    },
    {
        "title"    : "七海うらら『Øver Rider』MV(スマホゲーム『BLACK STELLA PTOLOMEA』主題歌)",
        "artist"   : "七海うらら*歌channel",
        "replays"  : 42,
        "thumbnail": "https://images-ext-1.discordapp.net/external/Y5O-1pCz1-tsnUi0Ez-dD-mnCRF4WtdoG-WtL0hcXyw/%3Fsqp%3D-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD%26rs%3DAOn4CLAaicehaeyx9U3kFvuas_1cJlDOXA/https/i.ytimg.com/vi/8M3geFKQ-hU/hq720.jpg?format=webp&width=574&height=323",
    },
]

title = "リスタルミュージック"
description = "本月最も再生された曲"
create_timer = time.time()
poster = create_top_songs_poster(
    songs,
    title,
    description,
    detail_texts=["41時間+", "1871曲再生しました", "18% アステル・レダ"],
)
print(f"Created poster, {time.time() - create_timer}ms")
cv2.imshow("Poster", poster)
cv2.imwrite("poster.png", poster)
cv2.waitKey(0)
cv2.destroyAllWindows()
