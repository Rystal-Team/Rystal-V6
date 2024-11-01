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

create_statement = {
    "sqlite": {
        "voice_rooms": {
            "create": """
                CREATE TABLE IF NOT EXISTS voice_rooms (
                    channel_id TEXT NOT NULL, 
                    member_limit TEXT NOT NULL, 
                    owner_id TEXT NOT NULL, 
                    guild_id TEXT NOT NULL,
                    locked BOOLEAN NOT NULL
                )
            """,
            "columns": {
                "channel_id": "TEXT NOT NULL",
                "member_limit": "TEXT NOT NULL",
                "owner_id": "TEXT NOT NULL",
                "guild_id": "TEXT NOT NULL",
                "locked": "BOOLEAN NOT NULL",
            },
        },
    },
    "mysql": {
        "voice_rooms": {
            "create": """
                CREATE TABLE IF NOT EXISTS voice_rooms (
                    channel_id VARCHAR(255) NOT NULL, 
                    member_limit VARCHAR(255) NOT NULL, 
                    owner_id VARCHAR(255) NOT NULL, 
                    guild_id VARCHAR(255) NOT NULL,
                    locked BOOLEAN NOT NULL
                )
            """,
            "columns": {
                "channel_id": "VARCHAR(255) NOT NULL",
                "member_limit": "VARCHAR(255) NOT NULL",
                "owner_id": "VARCHAR(255) NOT NULL",
                "guild_id": "VARCHAR(255) NOT NULL",
                "locked": "BOOLEAN NOT NULL",
            },
        },
    },
}
