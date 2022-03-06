import tkinter as tk


class RightClicker:
    def __init__(self, out_class, event):

        self.out_class = out_class
        event.widget.focus_set()  # focusing on text widget
        event.widget.tag_add(
            "sel", "1.0", "end"
        )  # selecting everything from text widget

        menu = tk.Menu(None, tearoff=0, takefocus=0)
        menu.add_command(
            label="Copy",
            command=lambda e=event, txt="Copy": self.click_command(event, "Copy"),
        )
        menu.tk_popup(event.x_root + 40, event.y_root + 10, entry="0")

    def click_command(self, event, cmd):
        self.out_class.master.clipboard_clear()
        event.widget.event_generate(f"<<{cmd}>>")
        event.widget.tag_remove("sel", "1.0", "end")
