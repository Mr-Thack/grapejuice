from pathlib import Path
from typing import Optional, Type, TypeVar, List

from gi.repository import Gtk

HandlerType = TypeVar("HandlerType")


def handler(x):
    return x


class WidgetAccessor:
    _builder: Optional

    def __init__(self, builder):
        self._builder = builder

    def __getattr__(self, item) -> Optional[Gtk.Widget]:
        return self._builder.get_object(item)

    def __getitem__(self, item) -> Optional[Gtk.Widget]:
        return self._builder.get_object(item)


class NullWidgetAccessor(WidgetAccessor):
    def __init__(self):
        super().__init__(None)

    def __getattr__(self, _) -> Optional[Gtk.Widget]:
        return None

    def __getitem__(self, _) -> Optional[Gtk.Widget]:
        return None


class GtkBase:
    _widgets: WidgetAccessor
    _glade_path: Optional[Path] = None
    _builder: Optional = None
    _handlers: List[HandlerType] = None
    _root_widget_name: Optional[str] = None

    def __init__(
        self,
        glade_path: Optional[Path] = None,
        handler_class: Optional[Type[HandlerType]] = None,
        handler_instance: Optional[HandlerType] = None,
        root_widget_name: Optional[str] = None
    ):
        self._handlers = []

        self._glade_path = glade_path
        self._builder = self._create_builder()

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

        self._root_widget_name = root_widget_name

    def _create_builder(self) -> Optional[Gtk.Builder]:
        if self._glade_path is not None:
            builder = Gtk.Builder()
            builder.add_from_file(self._glade_path)

            return builder

        return None

    @property
    def widgets(self) -> WidgetAccessor:
        return self._widgets

    @property
    def root_widget(self) -> Optional[Gtk.Widget]:
        return self.widgets[self._root_widget_name]

    def __del__(self):
        if self._builder is not None:
            del self._builder
            self._builder = None
