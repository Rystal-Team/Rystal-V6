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

import os

import yaml
from nextcord import Color
from termcolor import colored

with open("config/config.yaml", "r", encoding="utf8") as file:
    config = yaml.safe_load(file)

USE_SQLITE = config["USE_SQLITE"]
SQLITE_PATH = config["SQLITE_PATH"]
DEBUG = config["DEBUG"]
status_text = config["status_text"]
default_language = config["default_language"]
multi_lang = config["multi_lang"]
use_informal_lang = config["use_informal_lang"]
use_ytdlp = config["use_ytdlp"]
theme_color = config["theme_color"]
max_note = config["max_note"]

type_color = {
    "success": Color.from_rgb(*config["type_color"]["success"]),
    "error": Color.from_rgb(*config["type_color"]["error"]),
    "warn": Color.from_rgb(*config["type_color"]["warn"]),
    "info": Color.from_rgb(*config["type_color"]["info"]),
    "list": Color.from_rgb(*config["type_color"]["list"]),
    "win": Color.from_rgb(*config["type_color"]["win"]),
    "lose": Color.from_rgb(*config["type_color"]["lose"]),
    "game": Color.from_rgb(*config["type_color"]["game"]),
}

error_log_channel_id = config["error_log_channel_id"]
bug_report_channel_id = config["bug_report_channel_id"]
bot_owner_id = config["bot_owner_id"]

enable_activity_logging = config["enable_activity_logging"]
logging_channe_id = config["logging_channe_id"]

lang = {}
lang_mapping = {}
lang_list = []

lang_dirs = ["./lang"]
if use_informal_lang:
    lang_dirs.append("./lang/informal")

with open("./lang/en.yaml", "r", encoding="utf8") as stream:
    base_lang = yaml.safe_load(stream)

for lang_dir in lang_dirs:
    for filename in os.listdir(lang_dir):
        if filename.endswith(".yaml"):
            lang_name = filename[:-5]
            with open(f"{lang_dir}/{lang_name}.yaml", "r", encoding="utf8") as stream:
                lang_data = yaml.safe_load(stream)
                for key, value in base_lang.items():
                    if key not in lang_data:
                        print(
                            colored(
                                f"Language Missing Key: {key} in {lang_name}",
                                "red",
                            )
                        )
                        lang_data[key] = value
                lang[lang_name] = lang_data
                print(f"Loaded Language: {lang_name}")

for language in lang:
    lang_list.append(lang[language]["name"])
    lang_mapping[lang[language]["name"]] = language
