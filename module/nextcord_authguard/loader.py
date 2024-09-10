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

import yaml

from module.nextcord_authguard.permission import GeneralPermission


def load_permission(perm_config):
    """
    Load permissions from a YAML configuration file.

    Args:
        perm_config (str): Path to the YAML configuration file.

    Returns:
        dict: Parsed YAML data as a dictionary.
    """
    with open(perm_config, "r", encoding="utf8") as file:
        return yaml.safe_load(file)


def split_identifier(identifier):
    """
    Split an identifier string by '/'.

    Args:
        identifier (str): The identifier string to split.

    Returns:
        list: A list of substrings obtained by splitting the identifier.
    """
    return identifier.split("/")


def get_default_permission(default_perm, identifier) -> list:
    """
    Retrieve the default permissions for a given identifier.

    Args:
        default_perm (dict): The default permissions dictionary.
        identifier (str): The identifier string to look up permissions for.

    Returns:
        list: A list of GeneralPermission objects. Returns an empty list if no permissions are found.
    """
    permission = default_perm
    for part in split_identifier(identifier):
        permission = permission.get(part)
        if permission is None:
            return []
    return [GeneralPermission(perm) for perm in permission.split(",")]
