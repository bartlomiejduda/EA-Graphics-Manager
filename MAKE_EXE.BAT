
:: BAT script for making exe file
:: Created on 19.08.2021 by Bartlomiej Duda


@ECHO OFF
echo Starting make...
echo.
echo.

setlocal enabledelayedexpansion

set OUT_DIR="EA_Graphics_Manager_v0.7.3"

echo STEP 1
rm -rf dist 
rm -rf build 
rm -rf __pycache__
rm -rf !OUT_DIR!
rm -rf main.spec


echo STEP 2
mkdir !OUT_DIR!
set PYTHONOPTIMIZE=1 && pyinstaller --onedir -i .\img\icon_bd.ico --noupx .\main.py
xcopy ".\dist\main" "!OUT_DIR!\bin" /E /I
xcopy ".\img" "!OUT_DIR!\bin\img" /E /I
copy ".\docs\readme.txt" ".\!OUT_DIR!\readme.txt"
copy ".\LICENSE" ".\!OUT_DIR!\license.txt"
copy ".\RUN_PROGRAM.BAT" ".\!OUT_DIR!\RUN_PROGRAM.BAT"


echo STEP 3
rm -rf dist 
rm -rf build 
rm -rf __pycache__
rm -rf main.spec


echo Ending make...
pause