# -*- coding: utf-8 -*-

'''
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License 
'''





#legacy code 
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
    
    


