from grapejuice_common import variables
from grapejuice_common.gtk.gtk_base import GtkBase


class MainWindow(GtkBase):
    def __init__(self):
        super().__init__(glade_path=variables.grapejuice_glade())

        from gi.repository import Gtk
        self.widgets.main_window.connect("destroy", Gtk.main_quit)

    def show(self):
        self.widgets.main_window.show()
