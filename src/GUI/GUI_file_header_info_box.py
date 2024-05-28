import tkinter as tk

from src.GUI.right_clicker import RightClicker


class GuiFileHeaderInfoBox(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        self.file_header_labelframe = tk.LabelFrame(parent, text="File Header")
        self.file_header_labelframe.place(x=140, y=5, width=340, height=90)  # <-- file header box

        self.fh_label_sign = tk.Label(self.file_header_labelframe, text="Signature:", anchor="w")
        self.fh_label_sign.place(x=5, y=5, width=60, height=20)  # <-- signature label
        self.fh_text_sign = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_sign.place(x=70, y=5, width=80, height=20)  # <-- signature box
        self.fh_text_sign.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        self.fh_label_f_size = tk.Label(self.file_header_labelframe, text="File Size:", anchor="w")
        self.fh_label_f_size.place(x=5, y=35, width=60, height=20)  # <-- file size label
        self.fh_text_f_size = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_f_size.place(x=70, y=35, width=80, height=20)  # <-- file size box
        self.fh_text_f_size.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        self.fh_label_obj_count = tk.Label(self.file_header_labelframe, text="Object Count:", anchor="w")
        self.fh_label_obj_count.place(x=160, y=5, width=90, height=20)  # <-- object count label
        self.fh_text_obj_count = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_obj_count.place(x=250, y=5, width=80, height=20)  # <-- object count box
        self.fh_text_obj_count.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        self.fh_label_dir_id = tk.Label(self.file_header_labelframe, text="Format Ver.:", anchor="w")
        self.fh_label_dir_id.place(x=160, y=35, width=90, height=20)  # <-- directory id label
        self.fh_text_dir_id = tk.Text(
            self.file_header_labelframe,
            bg=self.file_header_labelframe["bg"],
            state="disabled",
        )
        self.fh_text_dir_id.place(x=250, y=35, width=80, height=20)  # <-- directory id box
        self.fh_text_dir_id.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))
