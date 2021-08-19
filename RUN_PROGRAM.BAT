
:: BAT script for running Python program

:: Ver    Date        Name
:: v0.1   19.08.2021  Bartlomiej Duda

@ECHO OFF
echo Starting execute...
echo.
echo.

setlocal enabledelayedexpansion

python main.py --windows-disable-console

echo Ending execute...
pause