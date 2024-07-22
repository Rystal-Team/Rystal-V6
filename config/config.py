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

import os

import yaml
from nextcord import Color

"""
=== BOT ===
"""
USE_SQLITE = False
SQLITE_PATH = "sqlite/database.db"
DEBUG = True
status_text = "🌟 v6.5.1a"
default_language = "en"
# Uses default language if multi_lang is set to false
# Use this if you have little memory
multi_lang = True
# Decide whether the bot would use ytdlp to extract video data (Slower when set to True)
# Set to True if the bot fails to extract video data.
use_ytdlp = False
# Color of rank card font etc
theme_color = "#2b67ab"
# The maximum amount of notes of each individual user.
# (A higher amount might increase the resource usage when fetching )
max_note = 500

"""
=== EMBEDs COLORS === 
"""
type_color = {
    "success": Color.from_rgb(157, 255, 158),
    "error": Color.from_rgb(255, 157, 157),
    "warn": Color.from_rgb(255, 206, 157),
    "info": Color.from_rgb(219, 157, 255),
    "list": Color.from_rgb(157, 200, 255),
}

"""
=== ADMINISTRATION === 
"""
# the channel id for error logging
error_log_channel_id = 1249810745735118889
# the user id of the owner of bot, or the person you want to have admin access to the bot
bot_owner_id = 699452241312219147

"""
=== ACTIVITY LOGGING (Logs all commands executed by users)=== 
I do not recommend turning this on as it does slow down the bot quite a bit
if you are running it on a low end server/computer, however if you really really 
want to then go ahead, the error logging should be more than enough though.!!!
"""
# whether you want activity logging or not, defaults to False
enable_activity_logging = False
# the channel id for logging (only required if activity logging is enabled, type None or "" if you don't need it)
logging_channe_id = 1203866958487879680

"""
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
==================================== DO NOT TOUCH ANYTHING BELOW!!! ====================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
========================================================================================================
"""
lang = {}
lang_mapping = {}
langs = []

if multi_lang:
    for filename in os.listdir("./lang"):
        if filename.endswith(".yaml"):
            filename = filename[:-5]
            with open(f"./lang/{filename}.yaml", "r", encoding="utf8") as stream:
                lang[filename] = yaml.safe_load(stream)
                print(f"Loaded Language: {filename}")
else:
    with open(f"./lang/{default_language}.yaml", "r", encoding="utf8") as stream:
        lang[default_language] = yaml.safe_load(stream)
        print(f"Loaded Language: {default_language}")

for language in lang:
    langs.append(lang[language]["name"])
    lang_mapping[lang[language]["name"]] = language
