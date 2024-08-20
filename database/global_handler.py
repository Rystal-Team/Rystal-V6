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


from .main_handler import db_handler


def get_global(name):
    query = {
        "sqlite": "SELECT value FROM global_settings WHERE name = ?",
        "mysql": "SELECT value FROM global_settings WHERE name = %s",
    }
    db_handler.execute(query[db_handler.db_type], (name,))
    return db_handler.fetchone()


def change_global(name, value):
    query = {
        "sqlite": "UPDATE global_settings SET value = ? WHERE name = ?",
        "mysql": "UPDATE global_settings SET value = %s WHERE name = %s",
    }
    db_handler.execute(query[db_handler.db_type], (value, name))
    db_handler.connection.commit()
    return
