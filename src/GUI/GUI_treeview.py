import tkinter as tk
from tkinter import ttk

from src.GUI.tree_manager import TreeManager


class GuiTreeView(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)
        style = ttk.Style()
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])  # get rid of the default treeview border
        style.configure("Treeview", indent=10)

        self.tree_frame = tk.Frame(
            parent,
            bg=parent["bg"],
            highlightbackground="grey",
            highlightthickness=1,
        )  # add custom treeview border
        self.tree_frame.place(x=10, y=10, width=120, height=380)

        self.treeview_widget = ttk.Treeview(self.tree_frame, show="tree", selectmode="browse")
        self.tree_man = TreeManager(self.treeview_widget)
        self.treeview_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.treeview_widget.bind("<Button-1>", gui_main.treeview_widget_select)
        self.treeview_widget.bind("<Button-3>", gui_main.treeview_widget_select)
