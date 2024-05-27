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
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.toolsmenu = tk.Menu(self.menubar, tearoff=0)
        gui_main.enable_swizzling_type2_menu_option = tk.BooleanVar()
        gui_main.enable_swizzling_type2_menu_option.set(True)
        gui_main.enable_swizzling_type91_menu_option = tk.BooleanVar()
        gui_main.enable_swizzling_type91_menu_option.set(False)
        self.toolsmenu.add_checkbutton(
            label="Enable Palette Swizzling (Type 2)",
            onvalue=1,
            offvalue=0,
            variable=gui_main.enable_swizzling_type2_menu_option,
        )
        self.toolsmenu.add_checkbutton(
            label="Enable Image Swizzling (Type 91)",
            onvalue=1,
            offvalue=0,
            variable=gui_main.enable_swizzling_type91_menu_option,
        )
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=lambda: gui_main.show_about_window())
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        parent.config(menu=self.menubar)
