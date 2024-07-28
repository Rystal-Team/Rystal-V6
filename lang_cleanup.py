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
import re


def find_used_keys(directory):
    """
    Recursively searches for and collects all keys used in Python files within the specified directory.

    Args:
        directory (str): The root directory to start the search.

    Returns:
        set: A set of keys found in the Python files.
    """
    used_keys = set()
    key_pattern = re.compile(r'"(.*?)"')
    for root, _, files in os.walk(directory):
        if ".venv" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    for line in f:
                        used_keys.update(key_pattern.findall(line))
    return used_keys


def cleanup_unused_keys(excluded_keys=None):
    """
    Identifies and optionally removes unused keys from YAML files in the './lang' directory.

    Args:
        excluded_keys (set, optional): A set of keys to exclude from the cleanup process. Defaults to None.
    """
    excluded_keys = excluded_keys or set()
    used_keys = find_used_keys("./")
    all_yaml_keys = set()
    yaml_files = []

    for root, _, files in os.walk("./lang"):
        for file in files:
            if file.endswith((".yaml", ".yml")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = []
                    for line in f:
                        lines.append(line)
                        match = re.match(r'^\s*"?(\w+)"?:', line)
                        if match:
                            all_yaml_keys.add(match.group(1))
                yaml_files.append((file_path, lines))

    unused_keys = all_yaml_keys - used_keys - excluded_keys

    if not unused_keys:
        print("No unused keys found.")
        return

    print("Unused keys:")
    for key in sorted(unused_keys):
        print(f"- {key}")

    if input("Remove all unused keys? (y/n): ").lower() == "y":
        unused_keys_set = set(unused_keys)
        for file_path, lines in yaml_files:
            with open(file_path, "w", encoding="utf-8") as f:
                for line in lines:
                    if not any(
                        re.match(rf'^\s*"?{key}"?:', line) for key in unused_keys_set
                    ):
                        f.write(line)
            print(f"Removed unused keys from {file_path}")


if __name__ == "__main__":
    excluded_keys = {
        "changed_volume",
        "volume_out_of_range",
        "author_only_interactions",
    }
    cleanup_unused_keys(excluded_keys)
