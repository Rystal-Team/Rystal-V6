"""import os, json, nextcord
from lyricsgenius import Genius
from module.embed import UpdateDropdownLyricsView


class Handler:
    @staticmethod
    async def search(interaction, song):
        users = [f"Line {i}" for i in range(1, 150)]
        L = 12

        print("Searching lyrics")

        async def get_page(page: int):
            emb = nextcord.Embed(title="The Users", description="")
            offset = (page - 1) * L
            for user in users[offset : offset + L]:
                emb.description += f"{user}\n"
            n = UpdateDropdownLyricsView.compute_total_pages(len(users), L)
            emb.set_footer(text=f"Page {page} from {n}")
            return emb, n

        await UpdateDropdownLyricsView(
            interaction,
            get_page,
            song
        ).navegate()
"""