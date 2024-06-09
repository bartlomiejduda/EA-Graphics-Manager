import tkinter as tk

from src.GUI.right_clicker import RightClicker


class GuiNewShapeFileHeaderInfoBox(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        # file header box
        self.file_header_labelframe = tk.LabelFrame(parent, text="File Header")
        self.file_header_labelframe.place(x=5, y=5, width=340, height=80)

        # signature label+box
        self.fh_label_sign = tk.Label(self.file_header_labelframe, text="Signature:", anchor="w")
        self.fh_label_sign.place(x=5, y=5, width=60, height=20)
        self.fh_text_sign = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_sign.place(x=70, y=5, width=80, height=20)
        self.fh_text_sign.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # file size label+box
        self.fh_label_f_size = tk.Label(self.file_header_labelframe, text="File Size:", anchor="w")
        self.fh_label_f_size.place(x=5, y=35, width=60, height=20)
        self.fh_text_f_size = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_f_size.place(x=70, y=35, width=80, height=20)  # <-- file size box
        self.fh_text_f_size.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # object count label+box
        self.fh_label_obj_count = tk.Label(self.file_header_labelframe, text="Object Count:", anchor="w")
        self.fh_label_obj_count.place(x=160, y=5, width=90, height=20)
        self.fh_text_obj_count = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_obj_count.place(x=250, y=5, width=80, height=20)
        self.fh_text_obj_count.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # header size label+box
        self.fh_label_header_size = tk.Label(self.file_header_labelframe, text="Header size:", anchor="w")
        self.fh_label_header_size.place(x=160, y=35, width=90, height=20)
        self.fh_text_header_size = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_header_size.place(x=250, y=35, width=80, height=20)
        self.fh_text_header_size.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))
