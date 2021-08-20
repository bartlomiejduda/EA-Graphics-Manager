
:: BAT script for running Python program

:: Ver    Date        Name
:: v0.1   19.08.2021  Bartlomiej Duda

@ECHO OFF
echo Executing program...
echo.
echo.

setlocal enabledelayedexpansion

python main.pyw --windows-disable-console

echo Ending program...