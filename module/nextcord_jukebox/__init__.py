"""
Nextcord-JukeBox: A lightweight Python library for Nextcord music bot.
"""

__title__ = "Nextcord-JukeBox"
__author__ = "Rystal-Team"
__license__ = "MIT"

import asyncio, threading, os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def initialize_logger():
    """
    Initializes and returns the Logger instance.

    Returns:
        Logger: An instance of the Logger class.
    """
    from .logger import Logger

    return Logger()


def initialize_rpc_handler():
    """
    Initializes and returns the RPC handler instance.

    Returns:
        RPCHandler: An instance of the RPCHandler class.
    """
    from .sockets import attach

    return attach()


# Initialize the logger and RPC handler
LogHandler = initialize_logger()
rpc_handler = initialize_rpc_handler()
