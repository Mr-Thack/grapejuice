from typing import Optional

from gi.repository import Gtk

from grapejuice_common import variables
from grapejuice_common.features.settings import current_settings
from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.gtk.gtk_base import GtkBase, handler
from grapejuice_common.wine.wineprefix_hints import WineprefixHint


class GtkWineprefixRow(Gtk.ListBoxRow):
    def __init__(self, prefix: WineprefixConfigurationModel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)

        icon_name = "gtk-home-symbolic"

        if WineprefixHint.studio in prefix.hints_as_enum:
            icon_name = "grapejuice-roblox-studio"

        elif WineprefixHint.player in prefix.hints_as_enum:
            icon_name = "grapejuice-roblox-player"

        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        image.set_margin_right(10)
        box.add(image)

        label = Gtk.Label()
        label.set_text(prefix.display_name)
        box.add(label)

        self.add(box)


class GtkAddWineprefixRow(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            orientation=Gtk.Orientation.HORIZONTAL,
            **kwargs
        )

        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.set_halign(Gtk.Align.CENTER)

        image = Gtk.Image.new_from_icon_name("add-symbolic", Gtk.IconSize.BUTTON)

        self.add(image)


class MainWindow(GtkBase):
    _current_page = None

    def __init__(self):
        super().__init__(
            glade_path=variables.grapejuice_glade(),
            handler_instance=self
        )

        from gi.repository import Gtk
        self.widgets.main_window.connect("destroy", Gtk.main_quit)

        self._populate_prefix_list()
        self._show_start_page()

    @handler
    def _show_start_page(self, *_, **__):
        self.widgets.prefix_list.unselect_all()
        self.set_page(self.widgets.cc_start_page)

    def _populate_prefix_list(self):
        listbox = self.widgets.prefix_list

        for child in listbox.get_children():
            listbox.remove(child)
            child.destroy()

        for prefix in current_settings.parsed_wineprefixes_sorted:
            row = GtkWineprefixRow(prefix)

            listbox.add(row)

        add_prefix_row = GtkAddWineprefixRow()

        listbox.add(add_prefix_row)

        listbox.show_all()

    def set_page(self, new_page: Optional = None, show_all: Optional[bool] = True):
        if self._current_page is not None:
            self.widgets.page_wrapper.remove(self._current_page)
            self._current_page = None

        if new_page is not None:
            self.widgets.page_wrapper.add(new_page)
            self._current_page = new_page

            if show_all:
                self._current_page.show_all()

    def show(self):
        self.widgets.main_window.show()
