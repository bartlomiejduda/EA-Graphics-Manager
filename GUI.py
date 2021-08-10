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



        self.butt1 = tk.Button(self.main_frame, text="OPEN", command=lambda: self.open_file() )
        self.butt1.place(x= 10, y= 50, width=60, height=20)       