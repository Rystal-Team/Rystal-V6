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
    """
    Creates a poster image with the top songs, including title, description, and optional details.

    Args:
        songs (List[dict]): List of dictionaries containing song information.
        title (str): Title of the poster.
        description (str): Description of the poster.
        detail_texts (Optional[List[str]]): Optional list of detail texts to include.

    Returns:
        np.ndarray: The generated poster image as a numpy array.
    """

    def draw_text(img, text, position, font_path, font_size, color, center=False):
        """
        Draws text on an image at a specified position with given font properties.

        Args:
            img (np.ndarray): The image to draw on.
            text (str): The text to draw.
            position (tuple): The (x, y) position to draw the text.
            font_path (str): Path to the font file.
            font_size (int): Size of the font.
            color (tuple): Color of the text in (R, G, B) format.
            center (bool): Whether to center the text at the position.

        Returns:
            np.ndarray: The image with the text drawn on it.
            tuple: The size of the drawn text.
        """
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
        """
        Draws a rounded rectangle on an image.

        Args:
            image (np.ndarray): The image to draw on.
            top_left (tuple): The (x, y) position of the top-left corner.
            bottom_right (tuple): The (x, y) position of the bottom-right corner.
            color (tuple): Color of the rectangle in (R, G, B) format.
            corner_radius (int): Radius of the corners.

        Returns:
            np.ndarray: The image with the rounded rectangle drawn on it.
        """
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
        """
        Draws a rounded rectangle on an image.

        Args:
            image (np.ndarray): The image to draw on.
            top_left (tuple): The (x, y) position of the top-left corner.
            bottom_right (tuple): The (x, y) position of the bottom-right corner.
            color (tuple): Color of the rectangle in (R, G, B) format.
            corner_radius (int): Radius of the corners.

        Returns:
            np.ndarray: The image with the rounded rectangle drawn on it.
        """
        if num < 1000:
            return str(num)
        for unit in ["", "k", "M", "B", "T"]:
            if abs(num) < 1000.0:
                return f"{num:3.1f}{unit}"
            num /= 1000.0

    def truncate_text(text_str: str, font_path, font_size, max_w) -> str:
        """
        Truncates text to fit within a specified width, adding ellipsis if necessary.

        Args:
            text_str (str): The text to truncate.
            font_path (str): Path to the font file.
            font_size (int): Size of the font.
            max_w (int): Maximum width for the text.

        Returns:
            str: The truncated text.
        """
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
        """
        Loads an image from a URL and returns it as a numpy array.

        Args:
            url (str): The URL of the image.

        Returns:
            np.ndarray: The loaded image as a numpy array.
        """
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            image = Image.open(BytesIO(resp.content)).convert("RGBA")
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)
        except (requests.RequestException, IOError):
            return np.zeros((200, 200, 4), dtype=np.uint8)

    def paste_image(background, overlay, x, y):
        """
        Pastes an overlay image onto a background image at a specified position.

        Args:
            background (np.ndarray): The background image.
            overlay (np.ndarray): The overlay image.
            x (int): The x-coordinate to paste the overlay.
            y (int): The y-coordinate to paste the overlay.

        Returns:
            np.ndarray: The background image with the overlay pasted on it.
        """
        y1, y2 = y, y + overlay.shape[0]
        x1, x2 = x, x + overlay.shape[1]
        alpha_s = overlay[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(0, 3):
            background[y1:y2, x1:x2, c] = (
                alpha_s * overlay[:, :, c] + alpha_l * background[y1:y2, x1:x2, c]
            )
        return background

    def get_thumbnail(thumbnails):
        """
        Retrieves the best thumbnail URL from a list of thumbnails.

        Args:
            thumbnails (list): List of thumbnail dictionaries.

        Returns:
            str: The URL of the best thumbnail.
        """
        return min(
            (
                thumb
                for thumb in thumbnails
                if (thumb["width"], thumb["height"]) != (120, 90)
            ),
            key=lambda t: t["width"] * t["height"],
            default="",
        )["url"]

    canvas = np.zeros((1300, 800, 3), dtype=np.uint8)
    canvas[:] = (29, 24, 22)

    font_paths = {
        "title": "./font/GoNotoKurrent-Bold.ttf",
        "description": "./font/GoNotoKurrent-Regular.ttf",
        "index": "./font/GoNotoKurrent-Regular.ttf",
        "song": "./font/GoNotoKurrent-Regular.ttf",
        "artist": "./font/GoNotoKurrent-Regular.ttf",
        "replay": "./font/GoNotoKurrent-Bold.ttf",
        "details": "./font/GoNotoKurrent-Regular.ttf",
    }

    logo = cv2.imread("./assets/logo.png", cv2.IMREAD_UNCHANGED)
    github_logo = cv2.imread("./assets/get-it-on-github.png", cv2.IMREAD_UNCHANGED)

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
            load_image_from_url(get_thumbnail(song["thumbnails"])),
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
