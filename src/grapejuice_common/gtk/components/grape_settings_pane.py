from typing import Optional, Iterable

from gi.repository import Gtk

from grapejuice_common.gtk.components.grape_settings_group import GrapeSettingsGroup


class GrapeSettingsPane(Gtk.ScrolledWindow):
    _viewport: Gtk.Viewport
    _box: Gtk.Box

    def __init__(
        self,
        *args,
        groups: Optional[Iterable[GrapeSettingsGroup]] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.set_hexpand(True)
        self.set_hexpand_set(True)
        self.set_vexpand(True)
        self.set_vexpand_set(True)
        self.set_min_content_height(550)

        self._viewport = Gtk.Viewport()
        self.add(self._viewport)

        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._viewport.add(self._box)

        if groups:
            for group in groups:
                self.add_group(group)

    def add_group(self, group: GrapeSettingsGroup) -> "GrapeSettingsPane":
        self._box.add(group)
        return self
