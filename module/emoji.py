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

import yaml
from nextcord import PartialEmoji
from config.loader import use_custom_emojis

emoji_dict = {}


def get_emoji(name):
    """
    Retrieve an emoji by name.

    Args:
        name (str): The name of the emoji to retrieve.

    Returns:
        PartialEmoji or None: The PartialEmoji object if custom emojis are used and found, otherwise None.
    """
    if use_custom_emojis:
        try:
            return PartialEmoji(id=emoji_dict.get(name), name=name)
        except Exception as e:
            raise Exception(f"Failed to get emoji: {e}")
    return emoji_dict.get(name)


def get_emoji_name(name):
    """
    Get the formatted emoji name.

    Args:
        name (str): The name of the emoji.

    Returns:
        str: The formatted emoji name.
    """
    return f"<:{name}:{emoji_dict.get(name)}>"


def load_dict():
    """
    Load the emoji dictionary from a YAML file.

    The file path is determined based on whether custom emojis are used.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    global emoji_dict
    file_path = "config/emojis.yaml" if use_custom_emojis else "config/emoji_map.yaml"
    with open(file_path, "r", encoding="utf-8") as file:
        emoji_dict = yaml.safe_load(file)
