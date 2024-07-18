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

from termcolor import colored


class Logger:
    LOG_LEVELS = {
        'DEBUG'   : logging.DEBUG,
        'INFO'    : logging.INFO,
        'WARNING' : logging.WARNING,
        'ERROR'   : logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def __init__(self, level='DEBUG'):
        """
        Initializes the Logger instance by setting up a logger with a specific name and configuring the console handler.

        Args:
            level (str): Logging level as a string. Default is 'DEBUG'.
        """
        name = "NEXTCORD_JUKEBOX"
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_logging_level(level))  # Set the logger level

        self._configure_console_handler()

    @property
    def __class__(self):
        return super().__class__

    def _get_logging_level(self, level_str):
        """
        Converts the logging level string to corresponding logging level constant.

        Args:
            level_str (str): Logging level as a string.

        Returns:
            int: Corresponding logging level constant.
        """
        return self.LOG_LEVELS.get(level_str, logging.DEBUG)  # Default to DEBUG if level_str is not found

    def _configure_console_handler(self):
        """
        Configures the console handler to output messages to the console with a specific formatter.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.logger.level)

        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def _color_message(self, level, message):
        """
        Colors the log message based on the log level.

        Args:
            level (str): The level of the log message.
            message (str): The message to log.

        Returns:
            str: The colored message.
        """
        colors = {
            'DEBUG'   : 'blue',
            'INFO'    : 'green',
            'WARNING' : 'yellow',
            'ERROR'   : 'red',
            'CRITICAL': 'magenta'
        }
        return colored(message, colors.get(level, 'white'))

    def set_level(self, level):
        """
        Sets the logging level dynamically.

        Args:
            level (str): The new logging level as a string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        """
        self.logger.setLevel(self._get_logging_level(level))
        for handler in self.logger.handlers:
            handler.setLevel(self.logger.level)

    def debug(self, message):
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        self.logger.debug(self._color_message('DEBUG', message))

    def info(self, message):
        """
        Logs an informational message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(self._color_message('INFO', message))

    def warning(self, message):
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(self._color_message('WARNING', message))

    def error(self, message):
        """
        Logs an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(self._color_message('ERROR', message))

    def critical(self, message):
        """
        Logs a critical message.

        Args:
            message (str): The message to log.
        """
        self.logger.critical(self._color_message('CRITICAL', message))
