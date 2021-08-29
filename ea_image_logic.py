# -*- coding: utf-8 -*-

'''
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License 
'''


# Program tested on Python 3.7.0

import os
import sys
import struct
from PIL import Image
import logger


class BMP_IMG:
    class BMP_HEADER:
        def __init__(self, in_size, in_offset):
            self.bmp_magic = b'BM'
            self.bmp_size = in_size
            self.reserved = 0
            self.offset_im_data = in_offset 
            
        def get_binary(self):
            return ( struct.pack("2s", self.bmp_magic) +
                     struct.pack("<L", self.bmp_size) +
                     struct.pack("<L", self.reserved) +  
                     struct.pack("<L", self.offset_im_data) 
                    )
        
    class BMP_INFO_HEADER:
        def __init__(self, in_width, in_height, in_bpp):
            self.info_header_size = 40
            self.num_of_planes = 1
            self.comp_type = 0
            self.comp_im_size = 0
            self.pref_hor_res = 0
            self.pref_vert_res = 0
            self.num_of_used_colors = 0
            self.num_of_imp_colors = 0
            
            self.im_width = in_width
            self.im_height = in_height 
            self.bpp = in_bpp 
            
        def get_binary(self):
            return ( struct.pack("<L", self.info_header_size) +
                     struct.pack("<L", self.im_width) +
                     struct.pack("<L", self.im_height) +
                     struct.pack("<H", self.num_of_planes) +
                     struct.pack("<H", self.bpp) +
                     struct.pack("<L", self.comp_type) +
                     struct.pack("<L", self.comp_im_size) +
                     struct.pack("<L", self.pref_hor_res) +
                     struct.pack("<L", self.pref_vert_res) +
                     struct.pack("<L", self.num_of_used_colors) +
                     struct.pack("<L", self.num_of_imp_colors)
                     )
        
    def __init__(self, in_width, in_height, in_bpp, in_image_data, in_palette_data):
        self.bmp_width = in_width
        self.bmp_height = in_height
        self.bmp_bpp = in_bpp
        self.bmp_data = in_image_data
        self.bmp_palette = in_palette_data
        
        self.data_size = len(self.bmp_data)
        self.palette_size = len(self.bmp_palette)
        self.bmp_size = 14 + 40 + self.palette_size + self.data_size
        self.data_offset = 14 + 40 + self.palette_size
        
        
        self.header = self.BMP_HEADER(self.data_size, self.data_offset)
        self.header_data = self.header.get_binary()
        
        self.info_header = self.BMP_INFO_HEADER(self.bmp_width, self.bmp_height, self.bmp_bpp)
        self.info_header_data = self.info_header.get_binary()
        
    def get_bmp_file_data(self):
        return ( self.header_data +
                 self.info_header_data + 
                 self.bmp_palette +
                 self.bmp_data
                )
        


class EA_IMAGE:
    
    class DIR_ENTRY:
        
        header_size = 16
        
        entry_types = {  
                         2:  "2 | 0x02 | SKEWED IMAGE",
                         33: "33 | 0x21 | PALETTE",
                         98: "98 | 0x62 | DXT5",
                         105: "105 | 0x69 | METAL BIN",
                         111: "111 | 0x6F | COMMENT",
                         112: "112 | 0x70 | IMG NAME",
                         124: "124 | 0x7C | HOT SPOT"
                      }
        
        def __init__(self, in_id, in_tag, in_offset):
            self.id = in_id
            self.tag = in_tag
            self.start_offset = in_offset
            self.end_offset = None
            self.raw_header = None 
            self.raw_data_offset = None
            self.raw_data = None
            self.bmp_image_data = None
            
            self.h_record_id = None
            self.h_size_of_the_block = None 
            self.h_width = None 
            self.h_height = None
            self.h_center_x = None 
            self.h_center_y = None 
            self.h_left_x_pos = None 
            self.h_top_y_pos = None 
            self.h_mipmaps_count = None 
            self.bin_attachments_list = []
            self.if_next_entry_exist_flag = None
            
        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)
            self.h_width = self.get_uint16(in_file, endianess)
            self.h_height = self.get_uint16(in_file, endianess)
            self.h_center_x = self.get_uint16(in_file, endianess)
            self.h_center_y = self.get_uint16(in_file, endianess)
            self.h_left_x_pos, unk1 = self.get_uint12_uint4(in_file, endianess)
            self.h_top_y_pos, self.h_mipmaps_count = self.get_uint12_uint4(in_file, endianess)

            
        def set_raw_data(self, in_file, in_data_start_offset, in_data_end_offset=0):
            zero_size_flag = -1
            
            if self.h_size_of_the_block == 0:
                zero_size_flag = 1
                self.h_size_of_the_block = in_data_end_offset - in_data_start_offset
            
            self.raw_data_offset = in_data_start_offset
            in_file.seek(self.raw_data_offset)
            
            if zero_size_flag == 1:
                self.if_next_entry_exist_flag = False
                self.raw_data = in_file.read(self.h_size_of_the_block)
            else:
                self.if_next_entry_exist_flag = True
                self.raw_data = in_file.read(self.h_size_of_the_block - self.header_size)
            
        def get_entry_type(self):
            result = self.entry_types.get(self.h_record_id, str(self.h_record_id) + " - UNKNOWN_TYPE")
            return result    
            
        def get_uint8(self, in_file, endianess):
            result = struct.unpack(endianess + "B", in_file.read(1))[0]
            return result
        
        def get_uint16(self, in_file, endianess):
            result = struct.unpack(endianess + "H", in_file.read(2))[0]
            return result
        
        def get_uint12_uint4(self, in_file, endianess):
            bytes2 = in_file.read(2)
            val_int = struct.unpack(endianess + "H", bytes2)[0]
            val_str = bin(val_int).lstrip('0b').zfill(16)
            
            uint4_str = val_str[0:4]
            uint4_int = int(uint4_str, 2)
            
            uint12_str = val_str[4:16]
            uint12_int = int(uint12_str, 2)
            
            out_list = [uint12_int, uint4_int]
            return out_list
        
        def get_uint24(self, in_file, endianess):
            if endianess == "<":
                result = struct.unpack(endianess + "I", in_file.read(3) + b'\x00')[0]
            else:
                result = struct.unpack(endianess + "I", b'\x00' + in_file.read(3))[0]
            return result   
        
        
        def get_uint32(self, in_file, endianess):
            result = struct.unpack(endianess + "L", in_file.read(4))[0]
            return result          
        
        def get_uint64(self, in_file, endianess):
            result = struct.unpack(endianess + "Q", in_file.read(8))[0]
            return result        
        
    class BIN_ATTACHMENT_ENTRY(DIR_ENTRY):
        
        entry_tags = {  
                         33: "palette 0x21",
                         105: "metal bin",
                         111: "comment",
                         112: "img name",
                         124: "hot spot"
                      }        
        
        def __init__(self, in_id, in_offset):
            self.id = in_id
            self.tag = None
            self.start_offset = in_offset
            self.end_offset = None
            self.raw_header = None 
            self.raw_data_offset = None
            self.raw_data = None
            
            self.h_record_id = None
            self.h_size_of_the_block = None 

            
        def set_tag(self, in_entry_id):
            self.tag = self.entry_tags.get(in_entry_id, str(in_entry_id) + " - UNKNOWN_TYPE")
                
            
    
    class METAL_BIN_ENTRY(BIN_ATTACHMENT_ENTRY):
        header_size = 16
        
        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)      
            self.h_data_size = self.get_uint16(in_file, endianess)
            self.h_flags = self.get_uint16(in_file, endianess)
            self.h_unknown = self.get_uint64(in_file, endianess)
            
    
    class COMMENT_ENTRY(BIN_ATTACHMENT_ENTRY):
        header_size = 8
        
        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)  
            self.h_comment_length = self.get_uint32(in_file, endianess) 
            
    class IMG_NAME_ENTRY(BIN_ATTACHMENT_ENTRY):
        header_size = 4
        
        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)  
            
    class HOT_SPOT_ENTRY(BIN_ATTACHMENT_ENTRY):
        header_size = 8
        
        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)  
            self.num_of_pairs = self.get_uint32(in_file, endianess)  

    class PALETTE_ENTRY(BIN_ATTACHMENT_ENTRY):
        header_size = 16
        
        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)  
            #TODO
  


     
    
    
    def __init__(self):
        self.sign = None
        self.total_f_size = -1
        self.num_of_entries = -1
        self.dir_id = None
        
        self.f_name = None
        self.f_path = None
        self.f_endianess = None
        self.f_endianess_desc = None
        self.f_size = None
        self.dir_entry_list = []
        self.ea_image_id = -1
        self.dir_entry_id = 0
        
        
        self.allowed_signatures = ( "SHPI", #PC games
                                    "SHPP", #PS1 games 
                                    "SHPS", #PS2 games
                                    "ShpX", "SHPX", #XBOX games
                                    "SHPM" #PSP games 
                                  )        
    
    
    def set_ea_image_id(self, in_ea_image_id):
        self.ea_image_id = in_ea_image_id
    
    def check_file_signature(self, in_file):
        try:
            sign = in_file.read(4).decode("utf8")
            in_file.seek(0)
            if sign not in self.allowed_signatures:
                raise
            return 0
        except:
            return -1   
        
    def parse_header(self, in_file, in_file_path, in_file_name):
        self.sign = in_file.read(4).decode("utf8")
        
        self.f_path = in_file_path
        self.f_name = in_file_name
        self.f_size = os.path.getsize(self.f_path)
        back_offset = in_file.tell()
        
        #check endianess & file validity
        self.total_f_size = struct.unpack( "<L", in_file.read(4) )[0]
        if self.total_f_size == self.f_size:
            self.f_endianess = "<"
            self.f_endianess_desc = "little"
        else:
            in_file.seek(back_offset)
            self.total_f_size = struct.unpack( ">L", in_file.read(4) )[0]
            if self.total_f_size == self.f_size:
                self.f_endianess = ">"
                self.f_endianess_desc = "big"
            else:
                logger.console_logger("Warning! Can't get file endianess! File may be broken! Using little endian as default!")
                self.f_endianess = "<"
                self.f_endianess_desc = "little"
        
        
        self.num_of_entries = struct.unpack( self.f_endianess + "L", in_file.read(4) )[0]
        self.dir_id = in_file.read(4).decode("utf8")
        
    def parse_directory(self, in_file):
        
        # creating directory entries
        for i in range(self.num_of_entries):
            self.dir_entry_id += 1
            entry_id = str(self.ea_image_id) + "_direntry_" + str(self.dir_entry_id)
            entry_tag = in_file.read(4).decode("utf8")
            entry_offset = struct.unpack( self.f_endianess + "L", in_file.read(4) )[0]
            ea_dir_entry = self.DIR_ENTRY(entry_id, entry_tag, entry_offset)
            
            self.dir_entry_list.append( ea_dir_entry ) #dir entry is now initialized and can be added to the list
            
         
        # updating end offset for each entry  
        # and parsing image data
        entry_num = 0
        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]
            entry_num += 1
            
            # set end offset for DIR entry
            if (entry_num == self.num_of_entries):
                ea_dir_entry.end_offset = self.total_f_size
            else:
                ea_dir_entry.end_offset = self.dir_entry_list[i+1].start_offset   
            
            in_file.seek(ea_dir_entry.start_offset)    
            self.parse_image_header_and_data(in_file, ea_dir_entry) 
            

            
    
    def parse_image_header_and_data(self, in_file, ea_dir_entry):
        ea_dir_entry.set_header(in_file, self.f_endianess) #read entry header and set all values 
        ea_dir_entry.set_raw_data(in_file, ea_dir_entry.start_offset, ea_dir_entry.end_offset) #read raw entry data and set values    
        
    def parse_bin_attachments(self, in_file):
        
        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]
            
            
            if (ea_dir_entry.if_next_entry_exist_flag is False and ea_dir_entry.start_offset + ea_dir_entry.h_size_of_the_block == ea_dir_entry.end_offset):
                pass # no binary attachments for this DIR entry
            else:
                
                # there are some binary attachments (1 or more)
                bin_att_id_count = 0
                in_file.seek(ea_dir_entry.start_offset + ea_dir_entry.h_size_of_the_block) # seek to offset of the first bin attachment
                
                while 1:
                    bin_att_start_offset = in_file.tell()
                    bin_att_id_count += 1
                    bin_att_id = ea_dir_entry.id + "_binattach_" + str(bin_att_id_count)
                    
                    bin_att_rec_id = struct.unpack(self.f_endianess + "B", in_file.read(1))[0]
                    in_file.seek(bin_att_start_offset)


                    if bin_att_rec_id == 105:
                        bin_att_entry = self.METAL_BIN_ENTRY(bin_att_id, bin_att_start_offset)
                    elif bin_att_rec_id == 111:
                        bin_att_entry = self.COMMENT_ENTRY(bin_att_id, bin_att_start_offset)
                    elif bin_att_rec_id == 112:
                        bin_att_entry = self.IMG_NAME_ENTRY(bin_att_id, bin_att_start_offset)
                    elif bin_att_rec_id == 124:
                        bin_att_entry = self.HOT_SPOT_ENTRY(bin_att_id, bin_att_start_offset)
                    else:
                        logger.console_logger("Unknown bin attachment entry! Aborting!")
                        break
                        
                    bin_att_entry.set_tag(bin_att_rec_id)
                    back_offset = in_file.tell()
                    bin_att_entry.set_header(in_file, self.f_endianess)
                    bin_att_entry.set_raw_data(in_file, in_file.tell(), ea_dir_entry.end_offset)
                    
                    bin_att_entry.start_offset = bin_att_start_offset
                    bin_att_entry.end_offset = in_file.tell()
                    
                    print("bin_att_id: ", bin_att_entry.id, "bin_att_tag: ", bin_att_entry.tag)
                    
                    ea_dir_entry.bin_attachments_list.append( bin_att_entry ) # binary attachment is now parsed
                                                                              # and can be added to the list
                    
                    
                    if bin_att_entry.end_offset >= ea_dir_entry.end_offset:
                        break  # no more binary attachment for this DIR entry
                    
        



def export_data(in_file_path, out_folder_path):
    '''
    Function for exporting data from EA graphics files
    '''    
    logger.console_logger("Starting export_data...")  
    
    if not os.path.exists(out_folder_path):
        os.makedirs(out_folder_path)      
    
    ssh_file = open(in_file_path, 'rb')
    
    try:
        magic = struct.unpack("4s", ssh_file.read(4))[0].decode("utf8")
    except:
        logger.console_logger("Can't read magic! Aborting!")
        return
        
    if magic not in ("SHPS", "SHPP", "SHPM"):
        logger.console_logger("It is not supported EA graphics file! Aborting!")
        return
    
    ssh_file.read(4) # total file size
    num_of_files = struct.unpack("<L", ssh_file.read(4))[0]
    ssh_file.read(4) # directory ID
    
    
    for f_count in range(num_of_files):
        file_name = struct.unpack("4s", ssh_file.read(4))[0].decode("utf8")
        file_offset = struct.unpack("<L", ssh_file.read(4))[0]

        back_offset = ssh_file.tell()
        ssh_file.seek(file_offset)
        
        #reading image header
        image_type = struct.unpack("<B", ssh_file.read(1))[0]
        im_bpp = -1
        block_size = struct.unpack("<L", ssh_file.read(3) + b'\x00')[0] - 16 
        if block_size < 0:
            block_size = 0
        im_width = struct.unpack("<H", ssh_file.read(2))[0] 
        im_height = struct.unpack("<H", ssh_file.read(2))[0]
        im_size_calc = im_width * im_height
        temp = ssh_file.read(8)
        
        im_data_offset = ssh_file.tell()
        pal_data_offset = im_data_offset + block_size
        

        print("file_name: " + str(file_name) +
              " image_type: " + str(image_type)
              )
                 
        
       
        ssh_file.seek(im_data_offset)
        
        
        if image_type == 2: # 8-bit skewed image with 256-colors swapped palette
            
            bmp_data = b'' # SKEW FIX
            temp_row = b''
            skew_val = im_width % 4      
            for i in range(im_height):
                temp_row = b''
                for j in range(im_width):
                    pixel = ssh_file.read(1)
                    temp_row += pixel
                if skew_val == 1:
                    temp_row += b'\x00\x00'
                elif skew_val == 2:
                    temp_row += b'x\00'
                    
                row_len = len(temp_row)
                bmp_data += temp_row
            
            diff = block_size - im_size_calc
            bmp_data += ssh_file.read(diff)
            
    
            #reading palette 
            ssh_file.seek(pal_data_offset)
            pal_header_data = ssh_file.read(15) # palette header
            palette_data = b''
            for i in range(256):
                pal_entry1 = ssh_file.read(1)
                pal_entry2 = ssh_file.read(1)
                pal_entry3 = ssh_file.read(1)
                pal_entry4 = ssh_file.read(1)
                palette_data += pal_entry4 + pal_entry3 + pal_entry2 + pal_entry1 # RGBA swap
                
            im_bpp = 8
            
            
        elif image_type == 64: # 4-bit image with 16-colors palette  
            im_size_calc = int((im_width * im_height) / 2)
            bmp_data = ssh_file.read(im_size_calc)   # TODO - find better samples and fix this
            
            
            ssh_file.read(15) # palette header 
            palette_data = ssh_file.read(16)
            im_bpp = 4
            
            
        elif image_type == 65: # 8-bit image with 256-colors palette (15 bits per color in palette)
            im_size = im_width * im_height
            bmp_data = ssh_file.read(im_size)
            ssh_file.read(16) # palette header
            palette_data = ssh_file.read(512)  # TODO - convert this 15-bit palette 
                                               # to 32-bit for BMP output
            im_bpp = 8           
                
        elif image_type == 66:  # 16-bit image (no palette)
            im_size = im_width * im_height * 2
            bmp_data = ssh_file.read(im_size)
            palette_data = b''
            im_bpp = 16
        
        elif image_type == 131: # refpack compressed 16-bpp image (no palette)
            im_size = block_size 
            bmp_data = ssh_file.read(im_size)  # TODO - use refpack decompressor
        
            
            
        else:
            logger.console_logger("Unsupported image type " + str(image_type) + "! Skipping!")
            ssh_file.seek(back_offset)
            continue
                      




        if image_type == 131:  # temporary data dump ( TODO - use refpack to handle this)
            out_file_path = out_folder_path + file_name.replace(">", "0") + "_" + str(f_count+1) + ".bin"
            out_file = open(out_file_path, "wb+")  
            out_file.write(bmp_data)
            out_file.close()            

        else:
            # writing bmp
            bmp_object = BMP_IMG(im_width, im_height, im_bpp, bmp_data, palette_data)
            bmp_file_data = bmp_object.get_bmp_file_data()
            out_file_path = out_folder_path + file_name.replace(">", "0") + "_" + str(f_count+1) + ".bmp"
            out_file = open(out_file_path, "wb+")  
            out_file.write(bmp_file_data)
            out_file.close()
        
        

        #BMP FLIP TOP BOTTOM FIX
        try:
            img = Image.open(out_file_path).transpose(Image.FLIP_TOP_BOTTOM)  
            img.save(out_file_path)
            img.close()
        except:
            logger.console_logger("Can't flip image " + file_name + "...")

        ssh_file.seek(back_offset)
    

    ssh_file.close()
    logger.console_logger("Ending export_data...")    
    
    
