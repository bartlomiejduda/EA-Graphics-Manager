import tkinter as tk
from src.logger import get_logger

logger = get_logger(__name__)


class RightClicker:
    def __init__(self, out_class, event):

        self.out_class = out_class
        self.text_box = event.widget
        text = event.widget.get("1.0", tk.END)[:-1]

        self.text_box.focus_set()  # focusing on text widget
        self.text_box.tag_add(
            "sel", "1.0", "end"
        )  # selecting everything from text widget

        menu = tk.Menu(None, tearoff=0, takefocus=0)
        menu.add_command(
            label="Copy",
            command=lambda e=event, txt="Copy": self.copy_text_to_clipboard(text),
        )
        menu.tk_popup(event.x_root + 40, event.y_root + 10, entry="0")

    def copy_text_to_clipboard(self, in_text):
        self.out_class.master.clipboard_clear()
        self.out_class.master.clipboard_append(in_text)
        self.text_box.tag_remove("sel", "1.0", "end")  # remove selection
