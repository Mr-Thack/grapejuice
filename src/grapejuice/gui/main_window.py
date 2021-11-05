import uuid
from typing import Optional

from gi.repository import Gtk

from grapejuice_common import variables
from grapejuice_common.features.settings import current_settings
from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.gtk.gtk_base import GtkBase
from grapejuice_common.wine.wineprefix_hints import WineprefixHint


class GtkListBoxRowWithIcon(Gtk.ListBoxRow):
    box: Gtk.Box

    def __init__(self, *args, icon_name: str = "security-low", **kwargs):
        super().__init__(*args, **kwargs)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)

        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        image.set_margin_right(10)
        box.add(image)

        self.box = box
        self.add(box)


class GtkWineprefixRow(GtkListBoxRowWithIcon):
    _prefix_model: WineprefixConfigurationModel = None

    def __init__(self, prefix: WineprefixConfigurationModel, *args, **kwargs):
        icon_name = "user-home-symbolic"

        if WineprefixHint.studio in prefix.hints_as_enum:
            icon_name = "grapejuice-roblox-studio"

        elif WineprefixHint.player in prefix.hints_as_enum:
            icon_name = "grapejuice-roblox-player"

        super().__init__(*args, icon_name=icon_name, **kwargs)

        self._prefix_model = prefix

        label = Gtk.Label()
        label.set_text(prefix.display_name)

        self.box.add(label)

    @property
    def prefix_model(self) -> WineprefixConfigurationModel:
        return self._prefix_model


class GtkStartUsingGrapejuiceRow(GtkListBoxRowWithIcon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, icon_name="user-home-symbolic", **kwargs)

        label = Gtk.Label()
        label.set_text("Start")

        self.box.add(label)


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

        image = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)

        self.add(image)


class MainWindow(GtkBase):
    _current_page = None

    def __init__(self):
        super().__init__(
            glade_path=variables.grapejuice_glade(),
            handler_instance=self
        )

        self.widgets.main_window.connect("destroy", Gtk.main_quit)
        self.widgets.prefix_list.connect("row-selected", self._prefix_row_selected)

        self._populate_prefix_list()
        self._show_start_page()

    def _show_start_page(self):
        self.set_page(self.widgets.cc_start_page)

    def _prefix_row_selected(self, _prefix_list, prefix_row):
        if isinstance(prefix_row, GtkWineprefixRow):
            self._show_prefix(prefix_row.prefix_model)

        elif isinstance(prefix_row, GtkStartUsingGrapejuiceRow):
            self._show_start_page()

        elif isinstance(prefix_row, Gtk.ListBoxRow):
            self._show_page_for_new_prefix()

    def _populate_prefix_list(self):
        listbox = self.widgets.prefix_list

        for child in listbox.get_children():
            listbox.remove(child)
            child.destroy()

        start_row = GtkStartUsingGrapejuiceRow()
        listbox.add(start_row)

        for prefix in current_settings.parsed_wineprefixes_sorted:
            row = GtkWineprefixRow(prefix)
            listbox.add(row)

        add_prefix_row = GtkAddWineprefixRow()
        listbox.add(add_prefix_row)

        listbox.show_all()

    def _show_prefix(self, prefix: WineprefixConfigurationModel):
        self.set_page(self.widgets.cc_prefix_page)
        self.widgets.prefix_name_label.set_text(prefix.display_name)

    def _show_page_for_new_prefix(self):
        model = WineprefixConfigurationModel(
            str(uuid.uuid4()),
            0,
            "gaming",
            "New Wineprefix",
            "",
            "",
            dict(),
            list()
        )

        self._show_prefix(model)

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
