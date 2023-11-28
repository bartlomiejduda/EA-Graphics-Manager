@echo off

set comtype_bms_path=.\ea_big4.bms
set input_folder_path=.\OUT
set output_folder_path=.\big_out


FOR /f %%f IN ('dir /s /b %input_folder_path%') DO (
	quickbms.exe -K -Y -o %comtype_bms_path% %%f %output_folder_path%
)

pause
