from imports import *


class NewEventHandler:
    def __init__(self):
        self.events: T.Dict[str, T.List[T.Callable]] = {}

    def register(self, event, callback):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(callback)

    def invoke(self, event, *args, **kwargs):
        if event not in self.events:
            warn(f'missing {event=}')
            return
        for callback in self.events[event]:
            try:
                callback(*args, **kwargs)
            except Exception as exc:
                if tk._default_root:
                    tk._default_root.report_callback_exception(type(exc), exc, exc.__traceback__)
                else:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)


EventHandler = NewEventHandler()
