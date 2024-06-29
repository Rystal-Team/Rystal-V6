"""
This module defines an EventListener class that manages event listeners, attaches cog instances, and fires events.

Classes:
    EventListener: A class for managing event listeners and dispatching events to attached cog instances.

Methods:
    listener(func): A decorator that registers a function as an event listener.
    attach(cog_instance): Attaches a cog instance to the EventListener.
    fire(event_name, *args, **kwargs): Fires an event, calling all registered listeners for the event.
"""

import inspect
from . import LogHandler

class EventListener:
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
        Attaches a cog instance to the EventListener.

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
                    if instance.__class__.__name__ == listener.__qualname__.split('.')[0]:
                        if inspect.iscoroutinefunction(listener):
                            await listener(instance, *args, **kwargs)
                        else:
                            listener(instance, *args, **kwargs)
