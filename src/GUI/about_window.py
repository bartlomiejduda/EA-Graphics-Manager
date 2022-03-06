import tkinter as tk
import center_tk_window

from src.logger import get_logger

logger = get_logger(__name__)


class AboutWindow:
    def __init__(self, gui_object):
        about_window = tk.Toplevel()
        about_window.wm_title("About")

        icon_dir = None
        try:
            icon_dir = gui_object.MAIN_DIRECTORY + "\\data\\img\\icon_bd.ico"
            about_window.iconbitmap(icon_dir)
        except tk.TclError:
            logger.error("Can't load the icon file from %s", icon_dir)

        a_text = (
            "EA Graphics Manager\n"
            "Version: " + gui_object.VERSION_NUM + "\n"
            "\n"
            "Program has been created\n"
            "by Bartłomiej Duda.\n"
            "\n"
            "If you want to support me,\n"
            "you can do it here:"
        )
        a_text2 = "https://www.paypal.me/kolatek55"
        a_text3 = "\n" "If you want to see my other tools,\n" + "go to my github page:"
        a_text4 = "https://github.com/bartlomiejduda"

        l = tk.Label(about_window, text=a_text)
        l.pack(side="top", fill="both", padx=10)
        l2 = tk.Label(about_window, text=a_text2, fg="blue", cursor="hand2")
        l2.bind("<Button-1>", lambda e: gui_object.web_callback(a_text2))
        l2.pack(side="top", anchor="n")
        l3 = tk.Label(about_window, text=a_text3)
        l3.pack(side="top", fill="both", padx=10)
        l4 = tk.Label(about_window, text=a_text4, fg="blue", cursor="hand2")
        l4.bind("<Button-1>", lambda e: gui_object.web_callback(a_text4))
        l4.pack(side="top", anchor="n")
        close_button = tk.Button(about_window, text="Close")
        close_button.pack()
        close_button.bind(
            "<Button-1>",
            lambda event, arg=about_window: gui_object.close_toplevel_window(arg),
        )

        center_tk_window.center_on_screen(about_window)
