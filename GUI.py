# -*- coding: utf-8 -*-

'''
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License 
'''





import os
import sys
import struct
import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu, filedialog, ttk, Text, LabelFrame, Radiobutton, Scrollbar
from PIL import ImageTk, Image
import webbrowser
import traceback
import pyperclip  # pip install pyperclip
from datetime import datetime
import tkinter.ttk as ttk



# Program tested on Python 3.7.0


#default app settings
WINDOW_HEIGHT = 350
WINDOW_WIDTH = 380

MIN_WINDOW_HEIGHT = WINDOW_HEIGHT
MIN_WINDOW_WIDTH = WINDOW_WIDTH  


class EA_MAN_GUI:
    def __init__(self, master, in_VERSION_NUM):
        self.master = master
        master.title("EA GRAPHICS MANAGER " + in_VERSION_NUM)
        master.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT) 

        self.search_file_path = ""
        self.search_file_name = ""
        self.search_file_flag = 0

        #main canvas
        self.canv1 = tk.Canvas(master, height=WINDOW_HEIGHT, width=WINDOW_WIDTH) 
        self.main_frame = tk.Frame(master, bg='#f0f0f0')
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)


        self.columns = ['a','b','c']
        self.treeview_widget = ttk.Treeview(self.main_frame, height = 20, columns = self.columns, show = 'headings')
        self.treeview_widget.place(x= 50, y= 70, width=200, height=200) 


        self.butt1 = tk.Button(self.main_frame, text="OPEN", command=lambda: self.open_file() )
        self.butt1.place(x= 10, y= 50, width=60, height=20)       
        
        
        # menu
        self.menubar = tk.Menu(master)
        
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open File", command=lambda: open_file())
        self.filemenu.add_command(label="Scan Directory", command=lambda: scan_dir())
        self.filemenu.add_command(label="Save as...", command=lambda: save_as())
        self.filemenu.add_command(label="Close File", command=lambda: close_font())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=master.destroy)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=lambda: show_about_window())
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        
        
        self.filemenu.entryconfig(2, state="disabled") 
        self.filemenu.entryconfig(3, state="disabled") 
        
        master.config(menu=self.menubar)        