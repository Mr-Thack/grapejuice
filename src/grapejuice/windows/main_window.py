import shutil
from typing import Optional, List, Callable

from gi.repository import Gtk, Gdk

from grapejuice import gui_task_manager, background
from grapejuice.components.main_window_components import \
    GrapeStartUsingGrapejuiceRow, \
    GrapeWineprefixRow, \
    GtkAddWineprefixRow
from grapejuice.tasks import \
    InstallRoblox, \
    OpenLogsDirectory, \
    ShowDriveC, \
    ExtractFastFlags
from grapejuice_common import variables
from grapejuice_common.features.settings import current_settings
from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.gtk.gtk_base import GtkBase, WidgetAccessor
from grapejuice_common.gtk.gtk_util import set_gtk_widgets_visibility, set_label_text_and_hide_if_no_text, \
    set_style_class_conditionally
from grapejuice_common.gtk.yes_no_dialog import yes_no_dialog
from grapejuice_common.util.computed_field import ComputedField
from grapejuice_common.wine.wine_functions import create_new_model_for_user
from grapejuice_common.wine.wineprefix import Wineprefix


class PrefixNameHandler:
    _wrapper = None
    _active_widget = None
    _prefix_name: str = ""
    _on_finish_editing_callbacks: List[Callable[["PrefixNameHandler"], None]]

    def __init__(self, prefix_name_wrapper):
        self._on_finish_editing_callbacks = []
        self._wrapper = prefix_name_wrapper

        label = Gtk.Label()
        label.set_text("__invalid__")
        self._label = label

        entry = Gtk.Entry()
        entry.connect("key-press-event", self._on_key_press)

        self._entry = entry

    def _on_key_press(self, _entry, event):
        key = Gdk.keyval_name(event.keyval)

        if key == "Return":
            self.finish_editing()

        elif key == "Escape":
            self.cancel_editing()

    def on_finish_editing(self, callback: Callable[["PrefixNameHandler"], None]):
        self._on_finish_editing_callbacks.append(callback)

    def finish_editing(self, use_entry_value: bool = True):
        self._set_active_widget(self._label)

        new_name = self._entry.get_text().strip()
        if not new_name:
            # Cannot use empty names
            use_entry_value = False

        if new_name == self.prefix_name:
            # No need to update
            use_entry_value = False

        if use_entry_value:
            self._prefix_name = new_name
            self._label.set_text(new_name)

            for cb in self._on_finish_editing_callbacks:
                cb(self)

    def _clear_active_widget(self):
        if self._active_widget is not None:
            self._wrapper.remove(self._active_widget)
            self._active_widget = None

    def _set_active_widget(self, widget):
        self._clear_active_widget()
        self._wrapper.add(widget)
        self._active_widget = widget
        widget.show()

    def set_prefix_name(self, name: str):
        self._set_active_widget(self._label)
        self._label.set_text(name)
        self._prefix_name = name

    def activate_entry(self):
        self._entry.set_text(self._prefix_name)
        self._set_active_widget(self._entry)
        self._entry.grab_focus()

    def cancel_editing(self):
        self.finish_editing(use_entry_value=False)

    @property
    def is_editing(self):
        return self._active_widget is self._entry

    @property
    def prefix_name(self) -> str:
        return self._prefix_name


def _open_fast_flags_for(prefix: Wineprefix):
    from grapejuice.windows.fast_flag_warning import FastFlagWarning

    def show_fast_flag_window():
        from grapejuice.windows.fast_flag_editor import FastFlagEditor

        fast_flag_editor = FastFlagEditor(prefix=prefix)
        fast_flag_editor.window.show()

    def warning_callback(confirmed: bool):
        if not confirmed:
            return

        task = ExtractFastFlags(prefix)
        background.tasks.add(task)

        gui_task_manager.wait_for_task(task, show_fast_flag_window)

    warning_window = FastFlagWarning(warning_callback)
    warning_window.show()


def _check_for_updates(widgets: WidgetAccessor):
    from grapejuice_common.update_info_providers import guess_relevant_provider

    update_provider = guess_relevant_provider()
    can_update = update_provider.can_update()

    # Hide the popover if Grapejuice cannot update itself
    set_gtk_widgets_visibility([widgets.update_popover], can_update)

    if not can_update:
        return

    class CheckForUpdates(background.BackgroundTask):
        def __init__(self, **kwargs):
            super().__init__("Checking for a newer version of Grapejuice", **kwargs)

        def work(self) -> None:
            show_button = False

            # Calculate info
            update_available = update_provider.update_available()

            if update_available:
                show_button = True
                update_status = "This version of Grapejuice is out of date."
                update_info = f"{update_provider.local_version()} -> {update_provider.target_version()}"

            else:
                if update_provider.local_is_newer():
                    update_status = "This version of Grapejuice is from the future"
                    update_info = f"\n{update_provider.local_version()}"

                else:
                    update_status = "Grapejuice is up to date"
                    update_info = str(update_provider.local_version())

            # Update Interface
            set_label_text_and_hide_if_no_text(widgets.update_status_label, update_status)
            set_label_text_and_hide_if_no_text(widgets.update_info_label, update_info)
            set_gtk_widgets_visibility([widgets.update_button], show_button)
            set_style_class_conditionally(
                [widgets.update_menu_button_image],
                "update-available-highlight",
                update_available
            )

    background.tasks.add(CheckForUpdates())


class MainWindow(GtkBase):
    _current_page = None
    _current_prefix_model: Optional[WineprefixConfigurationModel] = None
    _prefix_name_handler: PrefixNameHandler
    _current_prefix: ComputedField[Wineprefix]

    def __init__(self):
        super().__init__(glade_path=variables.grapejuice_glade())

        self._prefix_name_handler = PrefixNameHandler(self.widgets.prefix_name_wrapper)

        self._connect_signals()
        self._populate_prefix_list()
        self._show_start_page()

        self._current_prefix = ComputedField(
            lambda: None if self._current_prefix_model is None else Wineprefix(self._current_prefix_model)
        )

        _check_for_updates(self.widgets)

    def _save_current_prefix(self):
        if self._current_prefix_model is not None:
            current_settings.save_prefix_model(self._current_prefix_model)

    def _connect_signals(self):
        # General buttons
        self.widgets.main_window.connect("destroy", Gtk.main_quit)
        self.widgets.prefix_list.connect("row-selected", self._prefix_row_selected)

        # Prefix pane
        self.widgets.edit_prefix_name_button.connect("clicked", self._edit_prefix_name)
        self.widgets.install_roblox_button.connect(
            "clicked",
            lambda _b: gui_task_manager.run_task_once(InstallRoblox, self._current_prefix.value)
        )
        self.widgets.view_logs_button.connect(
            "clicked",
            lambda _b: gui_task_manager.run_task_once(OpenLogsDirectory)
        )
        self.widgets.drive_c_button.connect(
            "clicked",
            lambda _b: gui_task_manager.run_task_once(ShowDriveC, self._current_prefix.value)
        )
        self.widgets.fflags_button.connect(
            "clicked",
            lambda _b: _open_fast_flags_for(self._current_prefix.value)
        )

        self.widgets.create_prefix_button.connect(
            "clicked",
            lambda _b: self._create_current_prefix()
        )
        self.widgets.delete_prefix_button.connect(
            "clicked",
            lambda _b: self._delete_current_prefix()
        )

        # Dots menu
        self.widgets.about_grapejuice_button.connect(
            "clicked",
            lambda _b: self._show_about_window()
        )
        self.widgets.show_documentation_button.connect(
            "clicked",
            lambda _b: self._show_grapejuice_documentation()
        )

        def do_finish_editing_prefix_name(_handler):
            if self._current_prefix_model is not None:
                self._current_prefix_model.display_name = self._prefix_name_handler.prefix_name
                self._update_prefix_in_prefix_list(self._current_prefix_model)
                self._save_current_prefix()

        self._prefix_name_handler.on_finish_editing(do_finish_editing_prefix_name)

    def _show_about_window(self):
        self.widgets.dots_menu.popdown()

        from grapejuice.windows.about_window import AboutWindow
        wnd = AboutWindow()
        wnd.run()

        del wnd

    def _show_grapejuice_documentation(self):
        self.widgets.dots_menu.popdown()

        from grapejuice_common.util import xdg_open

        xdg_open(variables.git_wiki())

    def _show_start_page(self):
        self._set_page(self.widgets.cc_start_page)

    def _edit_prefix_name(self, _button):
        if self._prefix_name_handler.is_editing:
            self._prefix_name_handler.finish_editing()

        else:
            self._prefix_name_handler.activate_entry()

    def _prefix_row_selected(self, _prefix_list, prefix_row):
        if isinstance(prefix_row, GrapeWineprefixRow):
            self._show_prefix_model(prefix_row.prefix_model)

        elif isinstance(prefix_row, GrapeStartUsingGrapejuiceRow):
            self._show_start_page()

        elif isinstance(prefix_row, Gtk.ListBoxRow):
            self._show_page_for_new_prefix()

    def _populate_prefix_list(self):
        listbox = self.widgets.prefix_list

        for child in listbox.get_children():
            listbox.remove(child)
            child.destroy()

        start_row = GrapeStartUsingGrapejuiceRow()
        listbox.add(start_row)

        for prefix in current_settings.parsed_wineprefixes_sorted:
            row = GrapeWineprefixRow(prefix)
            listbox.add(row)

        add_prefix_row = GtkAddWineprefixRow()
        listbox.add(add_prefix_row)

        listbox.show_all()

    def _update_prefix_in_prefix_list(self, prefix: WineprefixConfigurationModel):
        for child in self.widgets.prefix_list.get_children():
            if isinstance(child, GrapeWineprefixRow):
                if child.prefix_model.id == prefix.id:
                    child.set_text(prefix.display_name)

    def _delete_current_prefix(self):
        model = self._current_prefix_model

        do_delete = yes_no_dialog(
            "Delete Wineprefix",
            f"Do you really want to delete the Wineprefix '{model.display_name}'?"
        )

        if do_delete:
            current_settings.remove_prefix_model(model)
            self._populate_prefix_list()
            self._show_start_page()

            shutil.rmtree(model.base_directory, ignore_errors=True)

    def _create_current_prefix(self):
        self._prefix_name_handler.finish_editing()

        model = self._current_prefix_model

        model.create_name_on_disk_from_display_name()
        current_settings.save_prefix_model(model)
        prefix = Wineprefix(model)

        def after_installation(_task):
            self._populate_prefix_list()
            self._show_prefix_model(self._current_prefix_model)

        gui_task_manager.run_task_once(
            InstallRoblox,
            prefix,
            on_finish_callback=after_installation
        )

    def _show_prefix_model(self, prefix: WineprefixConfigurationModel):
        self._current_prefix.clear_cached_value()
        self._set_page(self.widgets.cc_prefix_page)
        self._current_prefix_model = prefix
        self._prefix_name_handler.set_prefix_name(prefix.display_name)

        prefix_exists_on_disk = prefix.exists_on_disk

        set_gtk_widgets_visibility(
            [
                self.widgets.prefix_page_sep_0,
                self.widgets.prefix_action_buttons,
                self.widgets.delete_prefix_button
            ],
            prefix_exists_on_disk
        )

        set_gtk_widgets_visibility(
            [self.widgets.create_prefix_button],
            not prefix_exists_on_disk
        )

    def _show_page_for_new_prefix(self):
        model = create_new_model_for_user(current_settings.as_dict())

        if model.exists_on_disk:
            n = 1

            while model.exists_on_disk:
                model.display_name = f"New Wineprefix - {n}"
                model.create_name_on_disk_from_display_name()

                n += 1

        self._show_prefix_model(model)

    def _set_page(
        self,
        new_page: Optional = None,
        show_all: bool = True,
        clear_current_prefix: bool = True
    ):
        if self._current_page is not None:
            self.widgets.page_wrapper.remove(self._current_page)
            self._current_page = None

        if new_page is not None:
            self.widgets.page_wrapper.add(new_page)
            self._current_page = new_page

            if show_all:
                self._current_page.show_all()

        if clear_current_prefix:
            self._current_prefix_model = None

    def show(self):
        self.widgets.main_window.show()
