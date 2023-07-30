@echo off

rem Author: Bartlomiej Duda
rem Creation Date: 31.07.2023

set comtype_bms_path=refpack_script.bms
set input_folder_path=.\msh_out
set output_folder_path=.\msh_out


FOR /f %%f IN ('dir /b %input_folder_path%') DO (
	quickbms.exe -o %comtype_bms_path% %input_folder_path%\%%f %output_folder_path%
)

pause
