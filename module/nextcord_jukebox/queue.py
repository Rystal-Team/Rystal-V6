import asyncio
import concurrent.futures
import time

from meta_yt import Video
from termcolor import colored


class Queue:
    def __init__(self, loop):
        self.queue = []
        self.lock = asyncio.Lock()
        self.loop = loop
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

    async def add(self, song):
        self.queue.append(song)
        await asyncio.create_task(self._pre_extract())

    async def remove(self, song):
        if song in self.queue:
            self.queue.remove(song)
            print(colored(text=f"Removed {song.title} from the queue", color="green"))
            return True
        else:
            print(colored(text=f"{song.title} not found in the queue", color="red"))
            return False

    async def batch_add_to_queue(self, songs):
        self.queue.extend(songs)
        await asyncio.create_task(self._pre_extract())

    async def _pre_extract(self):
        async with self.lock:
            for song in self.queue:
                if not song.extracted_metadata:
                    await self.extract_metadata(song)

    async def extract_metadata(self, song):
        try:
            timer = time.time()
            video = await self.loop.run_in_executor(self.executor, Video, song.url)
            song.title = video.title
            song.views = video.views
            song.duration = video.duration
            song.thumbnail = video.thumbnail
            song.channel = video.channel
            song.channel_url = video.channel_url
            song.extracted_metadata = True
            print(colored(text=f"{song.title} [{song.url}]", color="magenta"))
            print(colored(text=f"Time taken: {time.time() - timer}", color="dark_grey"))
        except Exception as e:
            print(colored(f"Failed to extract {song.url}: {e}", color="red"))
        return
