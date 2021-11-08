import sys


def gtk_boot(main_function, *args, gtk_main=True, **kwargs):
    assert callable(main_function)
    sys.argv[0] = "Grapejuice"

    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

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
