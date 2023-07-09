from tkinter import ttk
import tkinter as tk


class GuiEntryPreview(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        self.preview_labelframe_width = 340
        self.preview_labelframe_height = 335
        self.preview_labelframe = tk.LabelFrame(parent, text="Preview")
        self.preview_labelframe.place(
            x=490,
            y=5,
            width=self.preview_labelframe_width,
            height=self.preview_labelframe_height,
        )