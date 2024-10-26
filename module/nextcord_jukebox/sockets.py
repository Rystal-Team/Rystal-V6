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
import json
import os
import threading
from typing import Dict, Optional

import websockets
from websockets.server import WebSocketServerProtocol

from . import LogHandler, __socket_standard_version__
from .event_manager import EventManager
from .exceptions import NothingPlaying


class RPCHandler(EventManager):
    """
    Handles WebSocket connections and dispatches events to clients.

    Attributes:
        clients (Dict[str, WebSocketServerProtocol]): A dictionary of connected clients.
        port (int): The port on which the WebSocket server listens.
        address (str): The address on which the WebSocket server listens.
        database: The database instance from the manager.
    """

    def __init__(self, manager) -> None:
        """
        Initializes the RPCHandler with the WebSocket server settings from environment variables.
        """
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.database = manager.database
        ws_port = os.getenv("RPC_WEBSOCKET_PORT")
        ws_address = os.getenv("RPC_WEBSOCKET_IP")

        if ws_port is not None:
            try:
                self.port: int = int(ws_port)
            except ValueError:
                raise ValueError("RPC_WEBSOCKET_PORT in .env file must be an integer")
        else:
            self.port = 8098

        self.address: str = ws_address if ws_address is not None else "localhost"

    @EventManager.listener
    async def track_start(self, player, interaction, before, after) -> None:
        """
        Event listener for when a track starts playing. Dispatches the track's information to connected clients.

        Args:
            player: The player instance.
            interaction: The interaction instance.
            before: The state before the event.
            after: The state after the event.
        """
        for member in player.members:
            if member == player.bot or member is None:
                continue
            user_secret: Optional[str] = await self.database.get_user_secret(member.id)
            if user_secret is not None:
                await self.dispatch(
                    user_secret,
                    {
                        "version": __socket_standard_version__,
                        "state"  : "playing",
                        "data"   : {
                            "title"    : after.title,
                            "url"      : after.url,
                            "channel"  : after.channel,
                            "thumbnail": after.thumbnail,
                        },
                    },
                )
            else:
                LogHandler.info(f"Client {member.global_name} not registered")

    @EventManager.listener
    async def queue_ended(self, player, interaction) -> None:
        """
        Event listener for when the queue ends. Dispatches an idle state to connected clients.

        Args:
            player: The player instance.
            interaction: The interaction instance.
        """
        for member in player.members:
            if member == player.bot or member is None or member == "None":
                continue
            user_secret: Optional[str] = await self.database.get_user_secret(member.id)
            if user_secret is not None:
                await self.dispatch(
                    user_secret,
                    {
                        "version": __socket_standard_version__,
                        "state"  : "idle",
                        "data"   : {},
                    },
                )
                LogHandler.info(
                    f"Dispatched queue_ended to {user_secret}[{member.global_name}]"
                )
            else:
                LogHandler.info(f"Client {member.global_name} not registered")

    @EventManager.listener
    async def member_joined_voice(self, player, member) -> None:
        """
        Event listener for when a member joins a voice channel. Dispatches the currently playing track to the client.

        Args:
            player: The player instance.
            member: The member who joined the voice channel.
        """
        if member == player.bot or member is None:
            return
        user_secret: Optional[str] = await self.database.get_user_secret(member.id)
        try:
            now_playing = await player.now_playing()
        except NothingPlaying:
            return
        if user_secret is not None:
            await self.dispatch(
                user_secret,
                {
                    "version": __socket_standard_version__,
                    "state"  : "playing",
                    "data"   : {
                        "title"    : now_playing.title,
                        "url"      : now_playing.url,
                        "channel"  : now_playing.channel,
                        "thumbnail": now_playing.thumbnail,
                    },
                },
            )
        else:
            LogHandler.info(f"Client {member.global_name} not registered")

    @EventManager.listener
    async def member_left_voice(self, player, member) -> None:
        """
        Event listener for when a member leaves a voice channel. Dispatches an idle state to the client.

        Args:
            player: The player instance.
            member: The member who left the voice channel.
        """
        if member == player.bot or member is None or member == "None":
            return
        user_secret: Optional[str] = await self.database.get_user_secret(member.id)
        if user_secret is not None:
            await self.dispatch(
                user_secret,
                {
                    "version": __socket_standard_version__,
                    "state"  : "idle",
                    "data"   : {},
                },
            )
            LogHandler.info(f"Dispatched idle to {user_secret}[{member.global_name}]")
        else:
            LogHandler.info(f"Client {member.global_name} not registered")

    async def handler(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """
        Handles incoming WebSocket connections and messages.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection instance.
            path (str): The path of the WebSocket connection.
        """
        secret: str = path.strip("/")
        self.clients[secret] = websocket
        LogHandler.info(f"Client {secret} connected")

        try:
            async for message in websocket:
                LogHandler.info(f"Received message from {secret}: {message}")
        except websockets.exceptions.ConnectionClosed as e:
            LogHandler.info(f"Client {secret} disconnected: {e}")
        finally:
            del self.clients[secret]

    async def dispatch(self, secret: str, data: dict) -> None:
        """
        Dispatches a message to a connected client.

        Args:
            secret (str): The client secret.
            data (dict): The data to be sent.
        """
        data = json.dumps(data)
        if secret in self.clients:
            await self.clients[secret].send(data)
            LogHandler.info(f"Dispatched message to client {secret}: {data}")
        else:
            LogHandler.info(f"Client {secret} not connected")

    async def start_server(self) -> None:
        """Starts the WebSocket server."""
        async with websockets.serve(self.handler, self.address, self.port):
            LogHandler.info(
                f"WebSocket server started on ws://{self.address}:{self.port}"
            )
            await asyncio.Future()


def start_websocket_server(handler: RPCHandler) -> None:
    """
    Starts the WebSocket server using the provided handler.

    Args:
        handler (RPCHandler): The handler instance to use for the WebSocket server.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(handler.start_server())
    loop.run_forever()


def attach(manager) -> RPCHandler:
    """
    Attaches the RPCHandler to the EventManager and starts the WebSocket server in a separate thread.

    Args:
        manager: The manager instance that provides the database and other services.

    Returns:
        RPCHandler: The attached handler instance.
    """
    handler = RPCHandler(manager)
    EventManager.attach(handler)
    websocket_thread = threading.Thread(target=start_websocket_server, args=(handler,))
    websocket_thread.start()
    return handler
