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

import requests
from PIL import Image, ImageDraw, ImageFont


def create_top_songs_poster(songs: List[dict], title: str, description: str,
                            detail_texts: Optional[List[str]] = None) -> Image:
    """
    Create a poster for top songs with given title, description, and optional details.

    Args:
        songs (List[dict]): A list of dictionaries, each containing "title", "artist", "replays", and "thumbnail" keys.
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
        for unit in ["", "k", "M", "B", "T"]:
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
        if url != "":
            return Image.open(BytesIO(requests.get(url).content)).convert("RGBA")
        return Image.new("RGBA", (200, 200), (0, 0, 0, 0))

    def get_smallest_thumbnail(thumbnails):
        if thumbnails == "":
            return ""
        min_dimensions = float("inf")
        min_url = ""
        for thumb in thumbnails:
            dimensions = thumb["width"] * thumb["height"]
            if dimensions < min_dimensions:
                print(f"Using size: {thumb['width']}x{thumb['height']}")
                min_dimensions = dimensions
                min_url = thumb["url"]
        return min_url

    canvas = Image.new("RGB", (800, 1300), color="#16181d")
    draw = ImageDraw.Draw(canvas)

    fonts = {name: ImageFont.truetype(f"font/GoNotoKurrent-{style}.ttf", size) for name, style, size in [
        ("title", "Bold", 36), ("description", "Regular", 28), ("index", "Regular", 20),
        ("song", "Regular", 28), ("artist", "Regular", 15), ("replay", "Bold", 25), ("details", "Regular", 24)
    ]}

    for path, pos, size in [
        ("assets/logo.png", (60, 90), (100, 100)),
        ("assets/get-it-on-github.png", (292, 1160), (215, 83))
    ]:
        canvas.paste(Image.open(path).resize(size), pos, Image.open(path).resize(size))

    draw.text((170, 95), title, font=fonts["title"], fill="#ffffff")
    draw.text((170, 140), description, font=fonts["description"], fill="#ffffff")
    draw.line((50, 250, 750, 250), fill="#1c1f26", width=3)

    details_x = 55
    for text in detail_texts or []:
        details_x += draw_rounded_text(text, fonts["details"], 15, 4, 15, (details_x, 205)) + 10

    for i, song in enumerate(songs):
        timer = time.time()
        y_pos = 260 + i * 90
        song_text = truncate_text(song["title"], fonts["song"], 540)
        artist_text = truncate_text(f"{song['artist']}", fonts["artist"], 540)
        replay_text = format_number(song["replays"]) if isinstance(song["replays"], int) else song["replays"]

        draw.text((50, y_pos + 22), str(i + 1), font=fonts["index"], fill="#576175")
        load_timer = time.time()
        thumbnail = load_image_from_url(get_smallest_thumbnail(song["thumbnails"])).resize((106, 60)).crop(
            (23, 0, 83, 60))
        print(f"Loaded IMG, time taken {time.time() - load_timer}ms")

        canvas.paste(thumbnail, (80, y_pos + 8), thumbnail)
        draw.text((150, y_pos + 5), song_text, font=fonts["song"], fill="#ffffff")
        draw.text((150, y_pos + 40), artist_text, font=fonts["artist"], fill="#97A8CB")
        draw.text((750, y_pos + 30), replay_text, font=fonts["replay"], fill="#ffffff", anchor="rm")

        if i < len(songs) - 1:
            draw.line((50, y_pos + 80, 750, y_pos + 80), fill="#1c1f26", width=2)
        print(f"Generated {i}, time taken {time.time() - timer}ms")

    draw.rectangle((750, 0, 800, 250), fill="#16181d")

    return canvas
