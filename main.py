# -*- coding: utf-8 -*-

'''
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License 
'''


# Program tested on Python 3.7.0

# Ver      Date        Author               Comment
# v0.1     23.01.2021  Bartlomiej Duda      -
# v0.2     28.01.2021  Bartlomiej Duda      -
# v0.3     30.01.2021  Bartlomiej Duda      -
# v0.4     31.01.2021  Bartlomiej Duda      Added BMP class
# v0.5     02.02.2021  Bartlomiej Duda      New image types partially reverse engineered
# v0.6     10.08.2021  Bartlomiej Duda      Added new modules, moved to new repository
# v0.6.2   13.08.2021  Bartlomiej Duda      Enhanced GUI
# v0.6.3   13.08.2021  Bartlomiej Duda      Enhanced GUI

VERSION_NUM = "v0.6.3"

import ea_image_logic
import tkinter as tk
import GUI
import center_tk_window    # pip install center_tk_window


    
def main():
    '''
    Main function of this program.
    '''   
    main_switch = 2
    # 1 - data export test
    # 2 - GUI test
    

    if main_switch == 1:
        p_in_file_path = "E:\\XENTAX\\EA SSH FSH Research\\EA SAMPLES\\NHL 2002 SSH\\awards.ssh"
        p_out_folder_path = "E:\\XENTAX\\EA SSH FSH Research\\EA SAMPLES\\NHL 2002 SSH\\awards.ssh_OUT\\"
              
        ea_image_logic.export_data(p_in_file_path, p_out_folder_path)
        
    elif main_switch == 2:
 
        
        #main window
        root = tk.Tk()
        ea_man_gui = GUI.EA_MAN_GUI(root, VERSION_NUM)
        center_tk_window.center_on_screen(root)
        root.mainloop()        
        
    else:
        bd_logger("Wrong option selected!")
        
        
    
    ea_image_logic.bd_logger("End of main...")    
    
    
    
main()