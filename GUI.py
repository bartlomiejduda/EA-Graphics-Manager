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
import datetime
import tkinter.ttk as ttk
import center_tk_window    # pip install center_tk_window
import ea_image_logic
import logger



# Program tested on Python 3.7.0


#default app settings
WINDOW_HEIGHT = 460
WINDOW_WIDTH = 450
MIN_WINDOW_HEIGHT = WINDOW_HEIGHT
MIN_WINDOW_WIDTH = WINDOW_WIDTH  
MAX_WINDOW_HEIGHT = WINDOW_HEIGHT
MAX_WINDOW_WIDTH = WINDOW_WIDTH


class EA_MAN_GUI:
            
    class RIGHT_CLICKER:
        def __init__(self, out_class, e):
            self.out_class = out_class
            commands = ["Copy"]
            menu = tk.Menu(None, tearoff=0, takefocus=0)
    
            for txt in commands:
                menu.add_command(label=txt, command=lambda e=e,txt=txt:self.click_command(e,txt))
    
            menu.tk_popup(e.x_root + 40, e.y_root + 10, entry="0")

        def click_command(self, e, cmd):
            self.out_class.master.clipboard_clear()
            e.widget.event_generate(f'<<{cmd}>>')   
       


    class TREE_MANAGER:
    
        class TREE_ITERATOR:
            def __iter__(self):
                self.a = 0
                return self
            
            def __next__(self):
                x = self.a
                self.a += 1
                return x       
          
        def __init__(self, in_widget):
            self.obj_count = 0
            self.objects_dict = {}
            self.id_iterator = iter(self.TREE_ITERATOR())
            self.tree_widget = in_widget
            
        def add_object(self, in_obj):
            obj_id = next(self.id_iterator)
            self.obj_count += 1
            in_obj.tree_id = obj_id
            self.tree_widget.insert('', tk.END, text=in_obj.f_name, iid=in_obj.tree_id, open=True)
            
            #add object children
            sub_id = 0
            for obj_dir_entry in in_obj.dir_entry_list:
                child_id = next(self.id_iterator)
                obj_dir_entry.id = child_id
                sub_id += 1
                self.tree_widget.insert('', tk.END, text=obj_dir_entry.tag, iid=obj_dir_entry.id, open=True)
                self.tree_widget.move(obj_dir_entry.id, in_obj.tree_id, sub_id)
            
        def remove_object(self, in_id):
            self.objects_dict.pop(in_id)
            
        def get_object(self, in_id):
            obj = self.objects_dict.get(in_id)
            return obj
      
      
    
    def __init__(self, master, in_VERSION_NUM):
        logger.console_logger("GUI init...")
        self.GUI_log_text = ""
        self.GUI_logger("GUI init...")
        self.master = master
        self.VERSION_NUM = in_VERSION_NUM
        master.title("EA GRAPHICS MANAGER " + in_VERSION_NUM)
        master.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT) 
        master.maxsize(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT) 
        
            
        self.allowed_filetypes = [ ('EA Graphics files', ['*.fsh', '*.psh', '*.ssh', '*.msh', '*.xsh']), 
                                   ('All files', ['*.*'])
                                 ]     
        
        self.allowed_signatures = ( "SHPI", #PC games
                                    "SHPP", #PS1 games 
                                    "SHPS", #PS2 games
                                    "ShpX", "SHPX", #XBOX games
                                    "SHPM" #PSP games 
                                  )

        #main frame
        self.main_frame = tk.Frame(master, bg='#f0f0f0')
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)


        #treeview widget
        style = ttk.Style()
        style.layout( "Treeview", [('Treeview.treearea', {'sticky': 'nswe'})] ) #get rid of the default border 
        
        self.tree_frame = tk.Frame(self.main_frame, bg=self.main_frame['bg'], highlightbackground="grey", highlightthickness=1) #add custom border
        self.tree_frame.place(x=10, y=10, width=120, height=435)   
        
        self.treeview_widget = ttk.Treeview(self.tree_frame, show="tree", selectmode="browse")
        self.tree_man = self.TREE_MANAGER(self.treeview_widget)
        self.treeview_widget.place(relx=0, rely=0, relwidth=1, relheight=1) 
        
        self.treeview_widget.bind("<<TreeviewSelect>>", self.treeview_widget_select)



        #header info
        self.file_header_labelframe = tk.LabelFrame(self.main_frame, text="File Header")
        self.file_header_labelframe.place(x=140, y=5, width=300, height=90)
        
        self.fh_label_sign = tk.Label(self.file_header_labelframe, text="Signature:", anchor="w")
        self.fh_label_sign.place(x=5, y=5, width=60, height=20)   
        self.fh_text_sign = tk.Text(self.file_header_labelframe, bg=self.file_header_labelframe['bg'], state="disabled")
        self.fh_text_sign.place(x=70, y=5, width=60, height=20)  
        self.fh_text_sign.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event) )
        
        
        #lambda event, arg=data: self.on_mouse_down(event, arg)
        
        self.fh_label_f_size = tk.Label(self.file_header_labelframe, text="File Size:", anchor="w")
        self.fh_label_f_size.place(x=5, y=35, width=60, height=20)   
        self.fh_text_f_size = tk.Text(self.file_header_labelframe, bg=self.file_header_labelframe['bg'], state="disabled")
        self.fh_text_f_size.place(x=70, y=35, width=60, height=20)  
        self.fh_text_f_size.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))
        
        self.fh_label_obj_count = tk.Label(self.file_header_labelframe, text="Object Count:", anchor="w")
        self.fh_label_obj_count.place(x=140, y=5, width=90, height=20)   
        self.fh_text_obj_count = tk.Text(self.file_header_labelframe, bg=self.file_header_labelframe['bg'], state="disabled")
        self.fh_text_obj_count.place(x=230, y=5, width=60, height=20)  
        self.fh_text_obj_count.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))
        
        self.fh_label_dir_id = tk.Label(self.file_header_labelframe, text="Directory ID:", anchor="w")
        self.fh_label_dir_id.place(x=140, y=35, width=90, height=20)   
        self.fh_text_dir_id = tk.Text(self.file_header_labelframe, bg=self.file_header_labelframe['bg'], state="disabled")
        self.fh_text_dir_id.place(x=230, y=35, width=60, height=20)
        self.fh_text_dir_id.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))
        
        
        #entry header
        self.entry_header_labelframe = tk.LabelFrame(self.main_frame, text="Entry Header")
        self.entry_header_labelframe.place(x=140, y=100, width=300, height=180)    
        
        self.eh_label_rec_id = tk.Label(self.entry_header_labelframe, text="Record Type:", anchor="w")
        self.eh_label_rec_id.place(x=5, y=5, width=80, height=20)   
        self.eh_text_rec_id = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_rec_id.place(x=90, y=5, width=200, height=20)  
        self.eh_text_rec_id.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))     
        
        self.eh_label_size_of_the_block = tk.Label(self.entry_header_labelframe, text="Size Of The Block:", anchor="w")
        self.eh_label_size_of_the_block.place(x=5, y=35, width=120, height=20)   
        self.eh_text_size_of_the_block = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_size_of_the_block.place(x=110, y=35, width=60, height=20)  
        self.eh_text_size_of_the_block.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))   
        
        self.eh_label_width = tk.Label(self.entry_header_labelframe, text="Width:", anchor="w")
        self.eh_label_width.place(x=5, y=65, width=80, height=20)   
        self.eh_text_width = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_width.place(x=70, y=65, width=60, height=20)  
        self.eh_text_width.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))    
        
        self.eh_label_height = tk.Label(self.entry_header_labelframe, text="Height:", anchor="w")
        self.eh_label_height.place(x=140, y=65, width=80, height=20)   
        self.eh_text_height = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_height.place(x=200, y=65, width=60, height=20)  
        self.eh_text_height.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))  
        
        self.eh_label_center_x = tk.Label(self.entry_header_labelframe, text="Center X:", anchor="w")
        self.eh_label_center_x.place(x=5, y=95, width=80, height=20)   
        self.eh_text_center_x = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_center_x.place(x=70, y=95, width=60, height=20)  
        self.eh_text_center_x.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))  
        
        self.eh_label_center_y = tk.Label(self.entry_header_labelframe, text="Center Y:", anchor="w")
        self.eh_label_center_y.place(x=140, y=95, width=80, height=20)   
        self.eh_text_center_y = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_center_y.place(x=200, y=95, width=60, height=20)  
        self.eh_text_center_y.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))   
        
        self.eh_label_left_x = tk.Label(self.entry_header_labelframe, text="Left X:", anchor="w")
        self.eh_label_left_x.place(x=5, y=125, width=80, height=20)   
        self.eh_text_left_x = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_left_x.place(x=70, y=125, width=60, height=20)  
        self.eh_text_left_x.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event)) 
        
        self.eh_label_left_y = tk.Label(self.entry_header_labelframe, text="Left Y:", anchor="w")
        self.eh_label_left_y.place(x=140, y=125, width=80, height=20)   
        self.eh_text_left_y = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_left_y.place(x=200, y=125, width=60, height=20)  
        self.eh_text_left_y.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))   
        
        
        #preview 
        self.preview_labelframe = tk.LabelFrame(self.main_frame, text="Preview")
        self.preview_labelframe.place(x=140, y=285, width=300, height=160)         

        
        # menu
        self.menubar = tk.Menu(master)
        
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open File", command=lambda: self.open_file(None), accelerator="Ctrl+O")
        master.bind_all("<Control-o>", self.open_file)
        self.filemenu.add_command(label="Scan Directory", command=lambda: self.scan_dir())
        self.filemenu.add_command(label="Save as...", command=lambda: self.save_as())
        self.filemenu.add_command(label="Close File", command=lambda: self.close_font())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=lambda: self.quit_program(None), accelerator="Ctrl+Q")
        master.bind_all("<Control-q>", self.quit_program)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        self.toolsmenu = tk.Menu(self.menubar, tearoff=0)
        self.toolsmenu.add_command(label="Show GUI Log", command=lambda: self.show_GUI_log())
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)        
        
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=lambda: self.show_about_window())
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        
        self.filemenu.entryconfig(1, state="disabled")
        self.filemenu.entryconfig(2, state="disabled") 
        self.filemenu.entryconfig(3, state="disabled") 
        
        master.config(menu=self.menubar)        
    
    
    def treeview_widget_select(self, event):
        item = self.treeview_widget.selection()[0]
        print("you clicked on", self.treeview_widget.item(item,"text"))
    
    
    def quit_program(self, event):
        logger.console_logger("Quit GUI...")
        self.master.destroy()
        
    def open_file(self, event):
        try:
            in_file = filedialog.askopenfile(filetypes=self.allowed_filetypes, mode='rb')  
            if in_file == None:
                return
            in_file_path = in_file.name 
            in_file_name = in_file_path.split("/")[-1]
        except Exception as e:
            print(e)
            messagebox.showwarning("Warning", "Failed to open file!")
            return
        
        try:
            sign = in_file.read(4).decode("utf8")
            in_file.seek(0)
            if sign not in self.allowed_signatures:
                raise
        except:
            messagebox.showwarning("Warning", "File not supported!")
            return
        
        logger.console_logger("Loading file " + in_file_name + "...")
        self.GUI_logger("Loading file " + in_file_name + "...")
        
        ea_img = ea_image_logic.EA_IMAGE()
        ea_img.parse_header(in_file, in_file_path, in_file_name)
        ea_img.parse_directory(in_file)

        #set text
        self.set_text_in_box(self.fh_text_sign, ea_img.sign)
        self.set_text_in_box(self.fh_text_f_size, ea_img.total_f_size)
        self.set_text_in_box(self.fh_text_obj_count, ea_img.num_of_entries)
        self.set_text_in_box(self.fh_text_dir_id, ea_img.dir_id)
        
        
        self.tree_man.add_object(ea_img)
        
        
        
    def set_text_in_box(self, in_box, in_text):
        in_box.config(state="normal")
        in_box.delete('1.0', tk.END)
        in_box.insert(tk.END, in_text)
        in_box.config(state="disabled")      
        
    def GUI_logger(self, in_str):
        now = datetime.datetime.now()
        new_log_str = now.strftime("%d-%m-%Y %H:%M:%S") + " " + in_str + "\n"
        self.GUI_log_text += new_log_str
        
            
    def show_GUI_log(self):
        log_window = tk.Toplevel(height=200, width=400)
        log_window.wm_title("GUI log")
        
        log_field = tk.Text(log_window)
        log_field.place(x=0, y=0, width=400, height=160)
        
        copy_button = tk.Button(log_window, text="Copy")
        copy_button.place(x=140, y=170, width=60, height=20)
        copy_button.bind('<Button-1>', lambda event, arg=log_field, arg2=log_window: self.copy_GUI_log_msg(arg, arg2, event))
        
        close_button = tk.Button(log_window, text="Close")
        close_button.place(x=210, y=170, width=60, height=20)     
        close_button.bind('<Button-1>', lambda event, arg=log_window: self.close_GUI_log(arg, event))
        
        self.set_text_in_box(log_field, self.GUI_log_text)
        
        center_tk_window.center_on_screen(log_window)
   
   
    def copy_GUI_log_msg(self, txt_field, wind, event):
        self.master.clipboard_clear()
        log_txt = txt_field.get("1.0",tk.END)
        self.master.clipboard_append(log_txt)
        messagebox.showinfo("Info", "Log has been copied to the clipboard!")
        wind.destroy()
   
    def close_GUI_log(self, wind, event):
        wind.destroy()
   
    def web_callback(self, url):
        webbrowser.open_new(url)   
        
    def show_about_window(self):
            t = tk.Toplevel()
            t.wm_title("About")
            
            a_text = ( "EA Graphics Manager\n"
                       "Version: " + self.VERSION_NUM + "\n"
                       "\n"
                       "Program has been created\n"
                       "by Bartłomiej Duda.\n"
                       "\n"
                       "If you want to support me,\n"
                       "you can do it here:" )        
            a_text2 = ( "https://www.paypal.me/kolatek55" )
            a_text3 = ( "\n"
                        "If you want to see my other tools,\n"
                        "go to my github page:" )
            a_text4 = ( "https://github.com/bartlomiejduda" )
            
            l = tk.Label(t, text=a_text)
            l.pack(side="top", fill="both", padx=10)
            l2 = tk.Label(t, text=a_text2, fg="blue", cursor="hand2")
            l2.bind("<Button-1>", lambda e: self.web_callback(a_text2))
            l2.pack(side="top", anchor='n')
            l3 = tk.Label(t, text=a_text3)
            l3.pack(side="top", fill="both", padx=10)        
            l4 = tk.Label(t, text=a_text4, fg="blue", cursor="hand2")
            l4.bind("<Button-1>", lambda e: self.web_callback(a_text4))
            l4.pack(side="top", anchor='n')    
        
            center_tk_window.center_on_screen(t)