

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

import asyncio
import datetime
from datetime import datetime, timedelta

from dbhandle import Database

# Get the current date and time
cutoff_date = (datetime.now() - timedelta(days=28)).timestamp()
print(cutoff_date)


def to_timestamp(dt):
    return int(dt.timestamp())


print(to_timestamp(datetime.now() - timedelta(days=500)))


async def test():
    db = Database(db_path="./jukebox.db")
    db.connect()
    await db.add_replay_entry("user1", (datetime.now() - timedelta(days=500)).isoformat(), "song 1")
    await db.add_replay_entry("user1", (datetime.now() - timedelta(days=500)).isoformat(), "song 2")
    await db.add_replay_entry("user1", (datetime.now() - timedelta(days=500)).isoformat(), "song 3")
    await db.add_replay_entry("user1", (datetime.now() - timedelta(days=29)).isoformat(), "song 4")
    await db.add_replay_entry("user1", (datetime.now() - timedelta(days=30)).isoformat(), "song 5")

    print(await db.get_replay_history("user1", cutoff_day=30))


if __name__ == "__main__":
    asyncio.run(test())
