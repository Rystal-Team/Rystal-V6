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

import inspect

from . import LogHandler


class EventManager:
    """
    A class for managing event listeners and dispatching events to attached cog instances.

    Attributes:
        _event_listeners (dict): A dictionary of event listeners keyed by event names.
        _cog_instances (list): A list of attached cog instances.
    """

    _event_listeners = {}
    _cog_instances = []

    @classmethod
    def listener(cls, func):
        """
        A decorator that registers a function as an event listener.

        Args:
            func (function): The function to register as an event listener.

        Returns:
            function: The registered function.
        """
        event_name = func.__name__
        if event_name not in cls._event_listeners:
            cls._event_listeners[event_name] = []
        cls._event_listeners[event_name].append(func)
        LogHandler.info(f"Started Listening on function {event_name}")
        return func

    @classmethod
    def attach(cls, cog_instance):
        """
        Attaches a cog instance to the EventManager.

        Args:
            cog_instance: The cog instance to attach.
        """
        cog_name = cog_instance.__class__.__name__
        cls._cog_instances.append(cog_instance)
        LogHandler.info(f"Attached cog {cog_name}")

    @classmethod
    async def fire(cls, event_name, *args, **kwargs):
        """
        Fires an event, calling all registered listeners for the event.

        Args:
            event_name (str): The name of the event to fire.
            *args: Positional arguments to pass to the event listeners.
            **kwargs: Keyword arguments to pass to the event listeners.
        """
        LogHandler.info(f"Fired {event_name}")
        for instance in cls._cog_instances:
            if event_name in cls._event_listeners:
                for listener in cls._event_listeners[event_name]:
                    if (
                        instance.__class__.__name__
                        == listener.__qualname__.split(".")[0]
                    ):
                        if inspect.iscoroutinefunction(listener):
                            await listener(instance, *args, **kwargs)
                        else:
                            listener(instance, *args, **kwargs)
