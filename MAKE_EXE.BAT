
:: BAT script for making exe file

:: Ver    Date        Name
:: v0.1   19.08.2021  Bartlomiej Duda
:: v0.2   20.08.2021  Bartlomiej Duda
:: v0.3   29.08.2021  Bartlomiej Duda

@ECHO OFF
echo Starting make...
echo.
echo.

setlocal enabledelayedexpansion

set OUT_DIR="EA_Graphics_Manager_v0.7.1"

echo STEP 1
rm -rf dist 
rm -rf build 
rm -rf __pycache__
rm -rf !OUT_DIR!
rm -rf main.spec



echo STEP 2
mkdir !OUT_DIR!
set PYTHONOPTIMIZE=1 && pyinstaller --onefile -i .\img\icon_bd.ico --splash .\img\loading.png --upx-dir c:\upx\ .\main.pyw
move .\dist\main.exe .\!OUT_DIR!\EA_Graphics_Manager.exe
xcopy ".\img" "!OUT_DIR!\img" /E /I
copy ".\docs\readme.txt" ".\!OUT_DIR!\readme.txt"
copy ".\LICENSE" ".\!OUT_DIR!\license.txt"

echo STEP 3
rm -rf dist 
rm -rf build 
rm -rf __pycache__
rm -rf main.spec


echo Ending make...
pause