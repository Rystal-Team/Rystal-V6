

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

class CustomCog:
    _event_listeners = {}
    _cog_instances = []

    @classmethod
    def event_listener(cls, func):
        event_name = func.__name__
        if event_name not in cls._event_listeners:
            cls._event_listeners[event_name] = []
        cls._event_listeners[event_name].append(func)
        return func

    @classmethod
    def add_cog(cls, cog_instance):
        cls._cog_instances.append(cog_instance)

    @classmethod
    def call_event(cls, event_name, *args, **kwargs):
        for instance in cls._cog_instances:
            if event_name in cls._event_listeners:
                for listener in cls._event_listeners[event_name]:
                    listener(instance, *args, **kwargs)


class MyCog(CustomCog):
    def __init__(self):
        self.started = False

    @CustomCog.event_listener
    def on_start(self):
        print(self.started)
        self.started = True
        print("Starting...")

    @CustomCog.event_listener
    def on_stop(self):
        print(self.started)
        self.started = False
        print("Stopping...")


# Trigger events from anywhere in your application
if __name__ == "__main__":
    my_cog = MyCog()

    # Register the cog instance
    CustomCog.add_cog(my_cog)

    # Trigger 'on_start' event globally
    CustomCog.call_event("on_start")

    # Trigger 'on_stop' event globally
    CustomCog.call_event("on_stop")
