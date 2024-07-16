"""
PlayerManager is responsible for managing MusicPlayer instances for different guilds in the bot. It handles the creation, retrieval, and removal of MusicPlayer instances, ensuring that each guild has a single player instance.

Attributes:
    players (dict): A dictionary mapping guild IDs to their respective MusicPlayer instances.
    bot (Bot): The bot instance to which the PlayerManager is attached.

Methods:
    __init__(bot):
        Initializes the PlayerManager with the given bot instance.

    get_player(interaction: Interaction, bot: BotIntegration) -> MusicPlayer:
        Retrieves the MusicPlayer for the guild associated with the given interaction. If no player exists, a new one is created and connected. Raises UserNotConnected if the user is not connected to a voice channel. Raises VoiceChannelMismatch if the user is in a different voice channel than the bot.

    remove_player(interaction: Interaction) -> bool:
        Removes the MusicPlayer for the guild associated with the given interaction. Returns True if a player was removed, False otherwise.

    fire_voice_state_update(member: Member, before, after) -> None:
        Handles voice state updates for the bot and other members, performing necessary actions such as removing the player if the bot leaves a voice channel.
"""

from nextcord import BotIntegration, Interaction, Member
from nextcord.utils import get

from .database_handler import Database
from .exceptions import UserNotConnected, VoiceChannelMismatch
from .music_player import MusicPlayer
from .replay_handler import attach as attach_replay
from .sockets import attach as attach_sockets


class PlayerManager(object):
    def __init__(self, bot, db_path: str = "./sqlite/jukebox.sqlite", enable_rpc: bool = True,
                 enable_replay: bool = True):
        """
        Initializes the PlayerManager with the given bot instance.

        Args:
            bot (Bot): The bot instance to which the PlayerManager is attached.
        """
        self.players = {}
        self.bot = bot
        self.database: Database = Database(db_path=db_path)
        self.database.connect()

        if enable_rpc:
            attach_sockets(self)
        if enable_replay:
            attach_replay(self)

    async def get_player(
        self, interaction: Interaction, bot: BotIntegration
    ) -> MusicPlayer:
        """
        Retrieves the MusicPlayer for the guild associated with the given interaction. If no player exists, a new one is created and connected.

        Args:
            interaction (Interaction): The interaction object containing information about the user and the guild.
            bot (BotIntegration): The bot integration instance.

        Returns:
            MusicPlayer: The MusicPlayer instance for the guild.

        Raises:
            UserNotConnected: If the user is not connected to a voice channel.
            VoiceChannelMismatch: If the user is in a different voice channel than the bot.
        """
        if not interaction.user.voice or not interaction.user.voice.channel:
            raise UserNotConnected

        if interaction.guild.id not in self.players:
            self.players[interaction.guild.id] = MusicPlayer(self, interaction, bot)
            await self.players[interaction.guild.id].connect(interaction)
        else:
            if not interaction.guild.voice_client:
                await self.players[interaction.guild.id].connect(interaction)
            elif (
                interaction.user.voice.channel
                != get(bot.voice_clients, guild=interaction.guild).channel
            ):
                raise VoiceChannelMismatch
        return self.players[interaction.guild.id]

    async def remove_player(self, interaction: Interaction) -> bool:
        """
        Removes the MusicPlayer for the guild associated with the given interaction.

        Args:
            interaction (Interaction): The interaction object containing information about the guild.

        Returns:
            bool: True if a player was removed, False otherwise.
        """
        if interaction.guild.id in self.players:
            await self.players[interaction.guild.id].cleanup()
            self.players.pop(interaction.guild.id, None)
            return True
        return False

    async def fire_voice_state_update(self, member: Member, before, after) -> None:
        """
        Handles voice state updates for the bot and other members, performing necessary actions such as removing the player if the bot leaves a voice channel.

        Args:
            member (Member): The member whose voice state is being updated.
            before (VoiceState): The previous voice state of the member.
            after (VoiceState): The new voice state of the member.
        """
        if member.id == self.bot.user.id:
            if before.channel is not None and after.channel is None:
                await self.remove_player(member)
        if member.guild.id in self.players:
            await self.players[member.guild.id]._on_voice_state_update(
                member, before, after
            )
        return
