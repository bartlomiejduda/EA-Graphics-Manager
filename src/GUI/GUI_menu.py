import tkinter as tk


class GuiMenu(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        self.menubar = tk.Menu(parent)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(
            label="Open File",
            command=lambda: gui_main.open_file(),
            accelerator="Ctrl+O",
        )
        parent.bind_all("<Control-o>", lambda x: gui_main.open_file())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=lambda: gui_main.quit_program(), accelerator="Ctrl+Q")
        parent.bind_all("<Control-q>", lambda x: gui_main.quit_program())

        # options submenu
        self.optionsmenu = tk.Menu(self.menubar, tearoff=0)
        self.mipmapsresamplingmenu = tk.Menu(self.optionsmenu, tearoff=0)
        self.optionsmenu.add_cascade(label="Mipmaps Resampling", menu=self.mipmapsresamplingmenu)
        self.mipmapsresamplingmenu.add_radiobutton(
            label="Nearest", variable=gui_main.current_mipmaps_resampling, value="nearest"
        )
        self.mipmapsresamplingmenu.add_radiobutton(
            label="Box", variable=gui_main.current_mipmaps_resampling, value="box"
        )
        self.mipmapsresamplingmenu.add_radiobutton(
            label="Bilinear", variable=gui_main.current_mipmaps_resampling, value="bilinear"
        )
        self.mipmapsresamplingmenu.add_radiobutton(
            label="Hamming", variable=gui_main.current_mipmaps_resampling, value="hamming"
        )
        self.mipmapsresamplingmenu.add_radiobutton(
            label="Bicubic", variable=gui_main.current_mipmaps_resampling, value="bicubic"
        )
        self.mipmapsresamplingmenu.add_radiobutton(
            label="Lanczos", variable=gui_main.current_mipmaps_resampling, value="lanczos"
        )

        # help submenu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=lambda: gui_main.show_about_window())

        # main menu
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Options", menu=self.optionsmenu)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        parent.config(menu=self.menubar)
