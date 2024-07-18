

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

import logging


class Logger:
    def __init__(self):
        """
        Initializes the Logger instance by setting up a logger with a specific name and configuring the console handler.
        """
        name = "nextcord_jukebox"
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG

        self._configure_console_handler()

    def _configure_console_handler(self):
        """
        Configures the console handler to output critical messages to the console with a specific formatter.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def debug(self, message):
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        self.logger.debug(message)

    def info(self, message):
        """
        Logs an informational message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def warning(self, message):
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Logs an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(message)

    def critical(self, message):
        """
        Logs a critical message.

        Args:
            message (str): The message to log.
        """
        self.logger.critical(message)


# Example usage
logger = Logger()
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
