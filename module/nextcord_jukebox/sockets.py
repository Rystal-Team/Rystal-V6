"""
This module implements an RPC (Remote Procedure Call) handler using WebSockets to manage communication between 
clients and a server. It includes methods for handling events, dispatching messages, and managing client connections.

Classes:
    RPCHandler: Handles WebSocket connections and dispatches events to clients.

Functions:
    start_websocket_server(handler): Starts the WebSocket server using the provided handler.
    attach(): Attaches the RPCHandler to the EventListener and starts the WebSocket server in a separate thread.

Modules:
    asyncio: Provides support for asynchronous programming.
    json: Handles JSON encoding and decoding.
    os: Provides a way to use operating system dependent functionality.
    threading: Constructs higher-level threading interfaces.
    websockets: Implements WebSocket servers and clients.
    .event_manager: Manages event listeners.
    .database_handler: Handles database connections and operations.
    .LogHandler: Manages logging functionalities.
"""

import os
import asyncio
import websockets
import threading
from .event_manager import EventListener
from . import LogHandler
from .database_handler import Database
import json

db = Database(db_path="./sqlite/user_secrets.sqlite")
db.connect()


class RPCHandler(EventListener):
    """
    Handles WebSocket connections and dispatches events to clients.

    Attributes:
        clients (dict): A dictionary of connected clients.
        port (int): The port on which the WebSocket server listens.
        address (str): The address on which the WebSocket server listens.
    """

    def __init__(self):
        """
        Initializes the RPCHandler with the WebSocket server settings from environment variables.
        """
        self.clients = {}
        ws_port = os.getenv("RPC_WEBSOCKET_PORT")
        ws_address = os.getenv("RPC_WEBSOCKET_IP")
        print(ws_port)
        if ws_port is not None:
            try:
                self.port = int(ws_port)
            except ValueError:
                raise ValueError("RPC_WEBSOCKET_PORT in .env file must be an integer")
        else:
            self.port = 8098

        if ws_address is not None:
            self.address = ws_address
        else:
            self.address = "localhost"

    @EventListener.listener
    async def track_start(self, player, interaction, before, after):
        """
        Event listener for when a track starts playing. Dispatches the track's information to connected clients.

        Args:
            player: The player instance.
            interaction: The interaction instance.
            before: The state before the event.
            after: The state after the event.
        """
        for member in player._members:
            if member == player.bot or member is None:
                continue
            user_secret = await db.get_user_secret(member.id)
            if user_secret is not None:
                await self.dispatch(
                    user_secret,
                    {
                        "state": "playing",
                        "data": {
                            "title": after.title,
                            "url": after.url,
                            "channel": after.channel,
                        },
                    },
                )

    @EventListener.listener
    async def queue_ended(self, player, interaction):
        """
        Event listener for when the queue ends. Dispatches an idle state to connected clients.

        Args:
            player: The player instance.
            interaction: The interaction instance.
        """
        for member in player._members:
            if member == player.bot or member is None:
                continue
            user_secret = await db.get_user_secret(member.id)
            if user_secret is not None:
                await self.dispatch(
                    user_secret,
                    {
                        "state": "idle",
                        "data": {},
                    },
                )
                LogHandler.info(
                    f"Dispatched queue_ended to {user_secret}[{member.global_name}]"
                )

    async def handler(self, websocket, path):
        """
        Handles incoming WebSocket connections and messages.

        Args:
            websocket: The WebSocket connection instance.
            path: The path of the WebSocket connection.
        """
        secret = path.strip("/")
        self.clients[secret] = websocket
        LogHandler.info(f"Client {secret} connected")

        try:
            async for message in websocket:
                LogHandler.info(f"Received message from {secret}: {message}")
        except websockets.exceptions.ConnectionClosed as e:
            LogHandler.info(f"Client {secret} disconnected: {e}")
        finally:
            del self.clients[secret]

    async def dispatch(self, secret, data):
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

    async def start_server(self):
        """
        Starts the WebSocket server.
        """
        async with websockets.serve(self.handler, self.address, self.port):
            LogHandler.info(
                f"WebSocket server started on ws://{self.address}:{self.port}"
            )
            await asyncio.Future()


def start_websocket_server(handler):
    """
    Starts the WebSocket server using the provided handler.

    Args:
        handler (RPCHandler): The handler instance to use for the WebSocket server.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(handler.start_server())
    loop.run_forever()


def attach():
    """
    Attaches the RPCHandler to the EventListener and starts the WebSocket server in a separate thread.

    Returns:
        RPCHandler: The attached handler instance.
    """
    handler = RPCHandler()
    EventListener.attach(handler)

    websocket_thread = threading.Thread(target=start_websocket_server, args=(handler,))
    websocket_thread.start()
    return handler
