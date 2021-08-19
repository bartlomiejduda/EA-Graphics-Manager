
:: BAT script for making exe file

:: Ver    Date        Name
:: v0.1   19.08.2021  Bartlomiej Duda

@ECHO OFF
echo Starting make...
echo.
echo.

setlocal enabledelayedexpansion

echo STEP 1
rm -rf main.build
rm -rf main.exe
rm -rf main.cmd

echo STEP 2
python -m nuitka --mingw64 main.py --windows-disable-console
rm -rf main.build
rm -rf main.cmd

echo Ending make...
pause