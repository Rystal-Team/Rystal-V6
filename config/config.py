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
}

error_log_channel_id = config["error_log_channel_id"]
bug_report_channel_id = config["bug_report_channel_id"]
bot_owner_id = config["bot_owner_id"]

enable_activity_logging = config["enable_activity_logging"]
logging_channe_id = config["logging_channe_id"]

lang = {}
lang_mapping = {}
langs = []

with open(f"./lang/en.yaml", "r", encoding="utf8") as stream:
    default_lang = yaml.safe_load(stream)

for filename in os.listdir("./lang"):
    if filename.endswith(".yaml"):
        lang_name = filename[:-5]
        with open(f"./lang/{lang_name}.yaml", "r", encoding="utf8") as stream:
            lang_data = yaml.safe_load(stream)
            for key, value in default_lang.items():
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
    langs.append(lang[language]["name"])
    lang_mapping[lang[language]["name"]] = language
