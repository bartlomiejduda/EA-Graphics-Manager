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
import io
import webbrowser
import traceback
import pyperclip  # pip install pyperclip
import datetime
import tkinter.ttk as ttk
import center_tk_window  # pip install center_tk_window
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
        def __init__(self, out_class, event):
            
            self.out_class = out_class
            event.widget.focus_set() #focusing on text widget
            event.widget.tag_add("sel","1.0","end") #selecting everything from text widget

            menu = tk.Menu(None, tearoff=0, takefocus=0)
            menu.add_command(label="Copy", command=lambda e=event,txt="Copy":self.click_command(event,"Copy"))
            menu.tk_popup(event.x_root + 40, event.y_root + 10, entry="0")
            

        def click_command(self, event, cmd):
            self.out_class.master.clipboard_clear()
            event.widget.event_generate(f'<<{cmd}>>')  
            event.widget.tag_remove("sel","1.0","end")
            

    class TREE_MANAGER:
         
        def __init__(self, in_widget):
            self.tree_widget = in_widget
            
        def add_object(self, in_obj):
            self.tree_widget.insert('', tk.END, text=in_obj.f_name, iid=in_obj.ea_image_id, open=True) # add file to tree, eg. "awards.ssh"
            
            # add object children (ea images) to tree
            sub_id = 0
            for dir_entry in in_obj.dir_entry_list:
                sub_id += 1
                self.tree_widget.insert('', tk.END, text=dir_entry.tag, iid=dir_entry.id, open=False)
                self.tree_widget.move(dir_entry.id, in_obj.ea_image_id, sub_id)
                
                # add binary attachments to tree
                bin_att_sub_id = 0
                for bin_att_entry in dir_entry.bin_attachments_list:
                    bin_att_sub_id += 1
                    self.tree_widget.insert('', tk.END, text=bin_att_entry.tag, iid=bin_att_entry.id, open=True)
                    self.tree_widget.move(bin_att_entry.id, dir_entry.id, bin_att_sub_id)     
                    
                
        def get_object(self, in_id, in_ea_images):
            for ea_img in in_ea_images:
                if int(in_id) == int(ea_img.ea_image_id):
                    return ea_img
            logger.console_logger("Warning! Couldn't find matching ea_img object!")
            
        def get_object_dir(self, in_ea_img, in_iid):
            for ea_dir in in_ea_img.dir_entry_list:
                if in_iid == ea_dir.id:
                    return ea_dir
            logger.console_logger("Warning! Couldn't find matching DIR object!")
            
        def get_object_bin_attach(self, in_dir_entry, in_iid):
            for bin_attach in in_dir_entry.bin_attachments_list:
                if in_iid == bin_attach.id:
                    return bin_attach
            logger.console_logger("Warning! Couldn't find matching BIN_ATTACHMENT object!")
            

      
      
    
    def __init__(self, master, in_VERSION_NUM):
        logger.console_logger("GUI init...")
        self.GUI_log_text = ""
        self.GUI_logger("GUI init...")
        self.master = master
        self.VERSION_NUM = in_VERSION_NUM
        master.title("EA GRAPHICS MANAGER " + in_VERSION_NUM)
        master.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT) 
        master.maxsize(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT) 
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            self.master.iconbitmap(self.current_dir + '\img\\icon_bd.ico')
        except:
            logger.console_logger("Can't load the icon file!")        
        
            
        self.allowed_filetypes = [ ('EA Graphics files', ['*.fsh', '*.psh', '*.ssh', '*.msh', '*.xsh']), 
                                   ('All files', ['*.*'])
                                 ]    
        
        self.ea_image_id = 0
        self.opened_ea_images_count = 0
        self.opened_ea_images = []

        #main frame
        self.main_frame = tk.Frame(master, bg='#f0f0f0')
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)


        #treeview widget
        style = ttk.Style()
        style.layout( "Treeview", [('Treeview.treearea', {'sticky': 'nswe'})] ) #get rid of the default treeview border 
        style.configure('Treeview', indent=10)
        
        self.tree_frame = tk.Frame(self.main_frame, bg=self.main_frame['bg'], highlightbackground="grey", highlightthickness=1) #add custom treeview border
        self.tree_frame.place(x=10, y=10, width=120, height=435)   
        
        self.treeview_widget = ttk.Treeview(self.tree_frame, show="tree", selectmode="browse")
        self.tree_man = self.TREE_MANAGER(self.treeview_widget)
        self.treeview_widget.place(relx=0, rely=0, relwidth=1, relheight=1) 
        
        self.treeview_widget.bind("<Button-1>", self.treeview_widget_select)
        self.treeview_widget.bind("<Button-3>", self.treeview_widget_select)
        

        #file header info
        self.file_header_labelframe = tk.LabelFrame(self.main_frame, text="File Header")
        self.file_header_labelframe.place(x=140, y=5, width=300, height=90)
        
        self.fh_label_sign = tk.Label(self.file_header_labelframe, text="Signature:", anchor="w")
        self.fh_label_sign.place(x=5, y=5, width=60, height=20)   
        self.fh_text_sign = tk.Text(self.file_header_labelframe, bg=self.file_header_labelframe['bg'], state="disabled")
        self.fh_text_sign.place(x=70, y=5, width=60, height=20)  
        self.fh_text_sign.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event) )
        
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
        
        
        #entry header info
        self.entry_header_labelframe = tk.LabelFrame(self.main_frame, text="Entry Header")
        self.entry_header_labelframe.place(x=140, y=100, width=300, height=180)    
        
        self.eh_label_rec_type = tk.Label(self.entry_header_labelframe, text="Record Type:", anchor="w")
        self.eh_label_rec_type.place(x=5, y=5, width=80, height=20)   
        self.eh_text_rec_type = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_rec_type.place(x=90, y=5, width=200, height=20)  
        self.eh_text_rec_type.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))     
        
        self.eh_label_size_of_the_block = tk.Label(self.entry_header_labelframe, text="Size Of The Block:", anchor="w")
        self.eh_label_size_of_the_block.place(x=5, y=35, width=120, height=20)   
        self.eh_text_size_of_the_block = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_size_of_the_block.place(x=110, y=35, width=60, height=20)  
        self.eh_text_size_of_the_block.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event)) 
        
        self.eh_label_mipmaps_count = tk.Label(self.entry_header_labelframe, text="Mipmaps:", anchor="w")
        self.eh_label_mipmaps_count.place(x=185, y=35, width=70, height=20)   
        self.eh_text_mipmaps_count = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_mipmaps_count.place(x=250, y=35, width=40, height=20)  
        self.eh_text_mipmaps_count.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))           
        
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
        
        self.eh_label_top_y = tk.Label(self.entry_header_labelframe, text="Top Y:", anchor="w")
        self.eh_label_top_y.place(x=140, y=125, width=80, height=20)   
        self.eh_text_top_y = tk.Text(self.entry_header_labelframe, bg=self.entry_header_labelframe['bg'], state="disabled")
        self.eh_text_top_y.place(x=200, y=125, width=60, height=20)  
        self.eh_text_top_y.bind('<Button-3>', lambda event, arg=self: self.RIGHT_CLICKER(arg, event))   
        
        
        #entry preview 
        self.preview_labelframe = tk.LabelFrame(self.main_frame, text="Preview")
        self.preview_labelframe.place(x=140, y=285, width=300, height=160)         

        
        # menu
        self.menubar = tk.Menu(master)
        
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open File", command=lambda: self.open_file(None), accelerator="Ctrl+O")
        master.bind_all("<Control-o>", self.open_file)
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
        
        
        master.config(menu=self.menubar)        
    
    
    def treeview_widget_select(self, event):
        item_iid = self.treeview_widget.identify_row(event.y)
        
        if item_iid == "": 
            return #quit if nothing is selected
        
        logger.console_logger("Loading item " + str(item_iid) + "...")
        
        item_id = item_iid.split("_")[0]
            
        
        ea_img = self.tree_man.get_object(item_id, self.opened_ea_images)
        
        
        #set text for header
        self.set_text_in_box(self.fh_text_sign, ea_img.sign)
        self.set_text_in_box(self.fh_text_f_size, ea_img.total_f_size)
        self.set_text_in_box(self.fh_text_obj_count, ea_img.num_of_entries)
        self.set_text_in_box(self.fh_text_dir_id, ea_img.dir_id)
        
        #set text for dir entry
        if "direntry" in item_iid and "binattach" not in item_iid:
            ea_dir = self.tree_man.get_object_dir(ea_img, item_iid)
            self.set_text_in_box(self.eh_text_rec_type, ea_dir.get_entry_type())
            self.set_text_in_box(self.eh_text_size_of_the_block, ea_dir.h_size_of_the_block)
            self.set_text_in_box(self.eh_text_mipmaps_count, ea_dir.h_mipmaps_count)
            self.set_text_in_box(self.eh_text_width, ea_dir.h_width)
            self.set_text_in_box(self.eh_text_height, ea_dir.h_height)
            self.set_text_in_box(self.eh_text_center_x, ea_dir.h_center_x)
            self.set_text_in_box(self.eh_text_center_y, ea_dir.h_center_y)
            self.set_text_in_box(self.eh_text_left_x, ea_dir.h_left_x_pos)
            self.set_text_in_box(self.eh_text_top_y, ea_dir.h_top_y_pos) 
            
            try:
                self.preview_instance.destroy()
            except:
                pass
            
            
            #image preview logic
            if ea_dir.is_img_convert_supported == True:
                try:
                    canv_height = 130
                    canv_width = 285
                    img_stream = io.BytesIO(ea_dir.img_convert_data)
                    pil_img = Image.open(img_stream).transpose(Image.FLIP_TOP_BOTTOM)   
                    
                    if pil_img.height > canv_height:
                        ratio = canv_height / pil_img.height
                        pil_img = pil_img.resize((int(pil_img.width * ratio), canv_height))    
                    
                    
                    self.ph_img = ImageTk.PhotoImage(pil_img)
                    
                    self.preview_instance = tk.Canvas(self.preview_labelframe, bg='white', width=canv_width, height=canv_height)
                    self.preview_instance.create_image(canv_width/2, canv_height/2, anchor="center", image=self.ph_img)
                    self.preview_instance.place(x=5, y=5)

                except Exception as e: 
                    logger.console_logger("Error occured while generating preview for " + str(item_iid) + "...")
                    print(e)
                    
            else:
                preview_text = "Preview for this image type is not supported..."
                self.preview_instance = tk.Label(self.preview_labelframe, text=preview_text, anchor="nw", justify="left", wraplength=300)
                self.preview_instance.place(x=5, y=5, width=285, height=130)                
            
            
        
        #set text and preview for bin attach entry    
        elif "binattach" in item_iid:
            dir_iid = item_iid.split("_binattach")[0]
            ea_dir = self.tree_man.get_object_dir(ea_img, dir_iid)
            bin_attach = self.tree_man.get_object_bin_attach(ea_dir, item_iid)
            self.set_text_in_box(self.eh_text_rec_type, bin_attach.get_entry_type())
            self.set_text_in_box(self.eh_text_size_of_the_block, bin_attach.h_size_of_the_block)   
            self.set_text_in_box(self.eh_text_mipmaps_count, "")
            self.set_text_in_box(self.eh_text_width, "")
            self.set_text_in_box(self.eh_text_height, "")
            self.set_text_in_box(self.eh_text_center_x, "")
            self.set_text_in_box(self.eh_text_center_y, "")
            self.set_text_in_box(self.eh_text_left_x, "")
            self.set_text_in_box(self.eh_text_top_y, "")
            
            
            try:
                self.preview_instance.destroy()
            except:
                pass
            

            if bin_attach.h_record_id in (33, 34, 35, 36, 41, 42, 45): # palette types
                pass #TODO - add preview for palettes
            elif bin_attach.h_record_id in (105, 111, 112, 124): # binary types
                #set hex preview
                preview_hex_string = bin_attach.raw_data.decode('utf8', 'backslashreplace').replace("\000", '.')[0:200] #limit preview to 200 characters
                self.preview_instance = tk.Label(self.preview_labelframe, text=preview_hex_string, anchor="nw", justify="left", wraplength=300)
                self.preview_instance.place(x=5, y=5, width=285, height=130) 
            else:
                logger.console_logger("Warning! Unknown binary attachment! Can't load preview!")
            
            
        else:
            self.set_text_in_box(self.eh_text_rec_type, "")
            self.set_text_in_box(self.eh_text_size_of_the_block, "")
            self.set_text_in_box(self.eh_text_mipmaps_count, "")
            self.set_text_in_box(self.eh_text_width, "")
            self.set_text_in_box(self.eh_text_height, "")
            self.set_text_in_box(self.eh_text_center_x, "")
            self.set_text_in_box(self.eh_text_center_y, "")
            self.set_text_in_box(self.eh_text_left_x, "")
            self.set_text_in_box(self.eh_text_top_y, "") 
            
            try:
                self.preview_instance.destroy()
            except:
                pass
            
        if event.num == 3:
            self.treeview_widget.selection_set(item_iid)
            self.treeview_rightclick_popup(event, item_iid)        
    
    
    
    def treeview_rightclick_popup(self, event, item_iid):
        #create right-click popup menu
        self.tree_rclick_popup = tk.Menu(self.master, tearoff=0)
        if "direntry" not in item_iid and "binattach" not in item_iid:
            self.tree_rclick_popup.add_command(label="Close File", command=lambda: self.treeview_rclick_close(item_iid))  
            self.tree_rclick_popup.tk_popup(event.x_root + 45, event.y_root + 10, entry="0")
        elif "direntry" in item_iid and "binattach" not in item_iid:
            self.tree_rclick_popup.add_command(label="Export Raw Image Data", command=lambda: self.treeview_rclick_export_raw(item_iid)) 
            #self.tree_rclick_popup.add_command(label="Export Image As BMP") 
            #self.tree_rclick_popup.add_command(label="Export Image Details As XML") 
            #self.tree_rclick_popup.add_command(label="Import Raw Image Data")
            #self.tree_rclick_popup.add_command(label="Import Image From BMP") 
           # self.tree_rclick_popup.add_command(label="Import Image Details From XML") 
            self.tree_rclick_popup.tk_popup(event.x_root + 85, event.y_root + 10, entry="0")
        elif "direntry" in item_iid and "binattach" in item_iid:
            self.tree_rclick_popup.add_command(label="Export Raw Binary Data", command=lambda: self.treeview_rclick_export_raw(item_iid)) 
            #self.tree_rclick_popup.add_command(label="Import Raw Binary Data")
            self.tree_rclick_popup.tk_popup(event.x_root + 85, event.y_root + 10, entry="0")
        else:
            logger.console_logger("Warning! Unsupported entry in right-click popup!")

      
    def treeview_rclick_close(self, item_iid):
        ea_img = self.tree_man.get_object(item_iid, self.opened_ea_images)
        self.treeview_widget.delete(item_iid)  #removing item from treeview
        del ea_img #removing object from memory
        
        self.set_text_in_box(self.fh_text_sign, "")
        self.set_text_in_box(self.fh_text_f_size, "")
        self.set_text_in_box(self.fh_text_obj_count, "")
        self.set_text_in_box(self.fh_text_dir_id, "")  
        
    def treeview_rclick_export_raw(self, item_iid):
        ea_img = self.tree_man.get_object(item_iid.split("_")[0], self.opened_ea_images)
        
        out_file = None
        try:
            out_file = filedialog.asksaveasfile(mode='wb+', defaultextension=".bin", 
                                            initialfile=ea_img.f_name + "_" + item_iid, 
                                            filetypes=( ("BIN files", "*.bin"), ("all files", "*.*")))
        except:
            messagebox.showwarning("Warning", "Failed to save file!")
        if out_file is None: 
            return   
        
        out_data = None 
        
        if "direntry" in item_iid and "binattach" not in item_iid:
            # get raw image data 
            ea_dir = self.tree_man.get_object_dir(ea_img, item_iid)
            out_data = ea_dir.raw_data
        elif "direntry" in item_iid and "binattach" in item_iid:
            # get raw bin attachment data
            dir_iid = item_iid.split("_binattach")[0]
            ea_dir = self.tree_man.get_object_dir(ea_img, dir_iid)
            bin_attach = self.tree_man.get_object_bin_attach(ea_dir, item_iid)  
            out_data = bin_attach.raw_data
        else:
            logger.console_logger("Warning! Unsupported entry while saving output binary data!")
        
        
        out_file.write(out_data)
        out_file.close()    
        messagebox.showinfo("Info", "File saved successfully!")
        
     
    
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
        
        ea_img = ea_image_logic.EA_IMAGE()
        check_result = ea_img.check_file_signature(in_file)
        
        if check_result != 0:
            messagebox.showwarning("Warning", "File not supported!")
            return
        
        logger.console_logger("Loading file " + in_file_name + "...")
        self.GUI_logger("Loading file " + in_file_name + "...")
        
        self.ea_image_id += 1
        self.opened_ea_images_count += 1  
        ea_img.set_ea_image_id(self.ea_image_id)
        self.opened_ea_images.append(ea_img)
        
        
        ea_img.parse_header(in_file, in_file_path, in_file_name)
        ea_img.parse_directory(in_file)  
        
        #check if there are any bin attachments 
        #and add them to the list if found
        ea_img.parse_bin_attachments(in_file)  
        
        #convert all supported images
        #in the ea_img file
        try:
            ea_img.convert_images()
        except Exception as e:
            print(e)
        

        #set text for header
        self.set_text_in_box(self.fh_text_sign, ea_img.sign)
        self.set_text_in_box(self.fh_text_f_size, ea_img.total_f_size)
        self.set_text_in_box(self.fh_text_obj_count, ea_img.num_of_entries)
        self.set_text_in_box(self.fh_text_dir_id, ea_img.dir_id)
        
        #set tex for the first entry
        self.set_text_in_box(self.eh_text_rec_type, ea_img.dir_entry_list[0].get_entry_type())
        self.set_text_in_box(self.eh_text_size_of_the_block, ea_img.dir_entry_list[0].h_size_of_the_block)
        self.set_text_in_box(self.eh_text_mipmaps_count, ea_img.dir_entry_list[0].h_mipmaps_count)
        self.set_text_in_box(self.eh_text_width, ea_img.dir_entry_list[0].h_width)
        self.set_text_in_box(self.eh_text_height, ea_img.dir_entry_list[0].h_height)
        self.set_text_in_box(self.eh_text_center_x, ea_img.dir_entry_list[0].h_center_x)
        self.set_text_in_box(self.eh_text_center_y, ea_img.dir_entry_list[0].h_center_y)
        self.set_text_in_box(self.eh_text_left_x, ea_img.dir_entry_list[0].h_left_x_pos)
        self.set_text_in_box(self.eh_text_top_y, ea_img.dir_entry_list[0].h_top_y_pos)


        self.tree_man.add_object(ea_img)
        
        in_file.close()
        
        
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
        
        try:
            log_window.iconbitmap('img\\icon_bd.ico')
        except:
            logger.console_logger("Can't load the icon file!")            
        
        log_field = tk.Text(log_window)
        log_field.place(x=0, y=0, width=400, height=160)
        
        copy_button = tk.Button(log_window, text="Copy")
        copy_button.place(x=140, y=170, width=60, height=20)
        copy_button.bind('<Button-1>', lambda event, arg=log_field, arg2=log_window: self.copy_GUI_log_msg(arg, arg2, event))
        
        close_button = tk.Button(log_window, text="Close")
        close_button.place(x=210, y=170, width=60, height=20)     
        close_button.bind('<Button-1>', lambda event, arg=log_window: self.close_toplevel_window(arg, event))
        
        self.set_text_in_box(log_field, self.GUI_log_text)
        
        center_tk_window.center_on_screen(log_window)
   
   
    def copy_GUI_log_msg(self, txt_field, wind, event):
        self.master.clipboard_clear()
        log_txt = txt_field.get("1.0",tk.END)
        self.master.clipboard_append(log_txt)
        messagebox.showinfo("Info", "Log has been copied to the clipboard!")
        wind.destroy()
   
    def close_toplevel_window(self, wind, event):
        wind.destroy()
   
    def web_callback(self, url):
        webbrowser.open_new(url)   
        
    def show_about_window(self):
            about_window = tk.Toplevel()
            about_window.wm_title("About")
            
            try:
                
                about_window.iconbitmap(self.current_dir + '\img\\icon_bd.ico')
            except:
                logger.console_logger("Can't load the icon file!")              
            
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
            
            l = tk.Label(about_window, text=a_text)
            l.pack(side="top", fill="both", padx=10)
            l2 = tk.Label(about_window, text=a_text2, fg="blue", cursor="hand2")
            l2.bind("<Button-1>", lambda e: self.web_callback(a_text2))
            l2.pack(side="top", anchor='n')
            l3 = tk.Label(about_window, text=a_text3)
            l3.pack(side="top", fill="both", padx=10)        
            l4 = tk.Label(about_window, text=a_text4, fg="blue", cursor="hand2")
            l4.bind("<Button-1>", lambda e: self.web_callback(a_text4))
            l4.pack(side="top", anchor='n') 
            close_button = tk.Button(about_window, text="Close")
            close_button.pack()
            close_button.bind('<Button-1>', lambda event, arg=about_window: self.close_toplevel_window(arg, event))
        
            center_tk_window.center_on_screen(about_window)
            
