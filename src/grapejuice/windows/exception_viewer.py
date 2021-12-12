import logging
from itertools import chain
from pathlib import Path
from typing import List, Optional, Iterable, Dict

from gi.repository import Gtk

from grapejuice_common import paths
from grapejuice_common.errors import PresentableError, format_exception
from grapejuice_common.gtk.gtk_base import GtkBase, handler
from grapejuice_common.gtk.gtk_paginator import GtkPaginator
from grapejuice_common.gtk.gtk_util import set_gtk_widgets_visibility
from grapejuice_common.gtk.yes_no_dialog import yes_no_dialog
from grapejuice_common.models.paginator import Paginator
from grapejuice_common.util import strip_pii
from grapejuice_common.util.event import Subscription

log = logging.getLogger(__name__)


def _exception_hash(ex: Exception):
    return hash(str(ex))


class ExceptionViewer(GtkBase):
    _exceptions: List[Exception]
    _tracebacks: Dict[int, str]
    _paginator: Paginator
    _gtk_paginator: GtkPaginator
    _paged_subscription: Optional[Subscription] = None
    _is_main: bool

    def __init__(
        self,
        exception: Optional[Exception] = None,
        exceptions: Optional[Iterable[Exception]] = None,
        is_main: Optional[bool] = False
    ):
        super().__init__(
            glade_path=paths.exception_viewer_glade(),
            handler_instance=self,
            root_widget_name="exception_viewer"
        )

        self._is_main = is_main

        self._exceptions = list(
            filter(
                None,
                chain(
                    [exception],
                    exceptions or []
                )
            )
        )

        if len(self._exceptions) <= 0:
            self._exceptions.append(PresentableError(
                title="No errors",
                description="The exception viewer was summoned, but no actual errors were reported to it. It looks "
                            "like the developer has made a mistake 😳",
                traceback_from_given_info=True
            ))

        single = "Grapejuice has run into a problem! Please check the details below."
        multiple = "Grapejuice has run into multiple problems! Please check the details below."
        self.widgets.problem_intro.set_text(single if len(self._exceptions) <= 1 else multiple)

        self._tracebacks = dict()
        for ex in self._exceptions:
            if isinstance(ex, PresentableError):
                tb = ex.traceback

            else:
                tb = format_exception(ex)

            tb = tb or "?! Something has gone wrong while getting the traceback"
            tb = strip_pii(tb)

            log.info(str(ex))
            log.info(tb)

            self._tracebacks[_exception_hash(ex)] = tb

        self._paginator = Paginator(collection=self._exceptions, page_size=1)
        self._gtk_paginator = GtkPaginator(self._paginator)
        self._paged_subscription = Subscription(self._paginator.paged, self._on_paged)

        self.widgets.pagination_container.add(self._gtk_paginator.root_widget)

        self._show_exception(self.current_exception)

    @handler
    def on_destroy(self, _window):
        if self._is_main:
            Gtk.main_quit()

    @handler
    def export_tracebacks(self, _button):
        dialog = Gtk.FileChooserDialog(
            title="Export error details",
            parent=self.root_widget,
            action=Gtk.FileChooserAction.SAVE
        )

        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()

        file_name: Optional[str] = None
        if response == Gtk.ResponseType.OK:
            file_name = dialog.get_filename()

        dialog.destroy()

        if file_name:
            self._do_export_tracebacks(file_name)

    def _do_export_tracebacks(self, file_name: str):
        from grapejuice_common.gtk.gtk_util import dialog

        if "." not in file_name:
            file_name = file_name + ".txt"

        path = Path(file_name).resolve()

        if path.exists():
            accept_overwrite = yes_no_dialog(
                title="File exists",
                message=f"The file '{path}' already exists, are you sure you want to overwrite it?"
            )

            if not accept_overwrite:
                dialog(f"Canceled write to '{path}' because the file already exists.")
                return

            log.info(f"User accepted file overwrite of {path}")

        tb_string = "\n\n".join(list(self._tracebacks.values()))

        try:
            with path.open("w+") as fp:
                fp.write(tb_string)

            dialog(f"Successfully saved error information to {path}")

        except Exception as e:
            # Can't catch a break
            log.error(str(e))

            # Use a regular dialog to prevent causing a self-loop
            dialog("Something went wrong while exporting the error information:\n\n" + str(e))

    @property
    def current_exception(self) -> Exception:
        return self._paginator.page[0]

    def _on_paged(self):
        self._show_exception(self.current_exception)

    def _show_exception(self, exception: Exception):

        if isinstance(exception, PresentableError):
            self.widgets.error_title.set_text(exception.title)
            self.widgets.error_description.set_text(exception.description)

        set_gtk_widgets_visibility(
            [self.widgets.error_title, self.widgets.error_description],
            isinstance(exception, PresentableError)
        )

        self.widgets.traceback_buffer.set_text(self._tracebacks[_exception_hash(exception)])

    def show(self):
        self.root_widget.show()

    def __del__(self):
        if self._paged_subscription:
            self._paged_subscription.unsubscribe()
            self._paged_subscription = None
