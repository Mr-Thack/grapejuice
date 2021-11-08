import sys


def gtk_boot(main_function, *args, gtk_main=True, **kwargs):
    assert callable(main_function)
    sys.argv[0] = "Grapejuice"

    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    from grapejuice_common.gtk.gtk_styling import load_style_from_path
    from grapejuice_common import variables
    load_style_from_path(variables.global_css())

    main_function(*args, **kwargs)

    if gtk_main:
        Gtk.main()


def dialog(dialog_text):
    from gi.repository import Gtk

    gtk_dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text=dialog_text
    )

    gtk_dialog.run()
    gtk_dialog.destroy()


def set_gtk_widgets_visibility(widgets, visible):
    for w in widgets:
        if visible:
            w.show()

        else:
            w.hide()


def set_label_text_and_hide_if_no_text(label, text):
    if text.strip():
        label.set_text(text)
        label.show()

    else:
        label.set_text("")
        label.hide()


def set_style_class_conditionally(widgets, style_class, condition):
    for w in widgets:
        style_context = w.get_style_context()
        method = style_context.add_class if condition else style_context.remove_class
        method(style_class)
