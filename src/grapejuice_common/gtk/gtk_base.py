from pathlib import Path
from typing import Optional, Type, TypeVar, List

HandlerType = TypeVar("HandlerType")


def handler(x):
    return x


class WidgetAccessor:
    _builder: Optional

    def __init__(self, builder):
        self._builder = builder

    def __getattr__(self, item):
        return self._builder.get_object(item)

    def __getitem__(self, item):
        return self._builder.get_object(item)


class NullWidgetAccessor(WidgetAccessor):
    def __init__(self):
        super().__init__(None)

    def __getattr__(self, _):
        return None

    def __getitem__(self, _):
        return None


class GtkBase:
    _widgets: WidgetAccessor
    _builder: Optional = None
    _handlers: List[HandlerType] = None

    def __init__(
        self,
        glade_path: Optional[Path] = None,
        handler_class: Optional[Type[HandlerType]] = None,
        handler_instance: Optional[HandlerType] = None
    ):
        self._handlers = []

        if glade_path is not None:
            from gi.repository import Gtk

            self._builder = Gtk.Builder()
            self._builder.add_from_file(glade_path)

        if self._builder is None:
            self._widgets = NullWidgetAccessor()

        else:
            if handler_class is not None:
                self._handlers.append(handler_class())

            if handler_instance is not None:
                self._handlers.append(handler_instance)

            for h in self._handlers:
                self._builder.connect_signals(h)

            self._widgets = WidgetAccessor(self._builder)

    @property
    def widgets(self) -> WidgetAccessor:
        return self._widgets
