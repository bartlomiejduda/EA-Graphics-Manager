
:: BAT script for making exe file
:: Created on 01.03.2022 by Bartlomiej Duda


@ECHO OFF
cd ..
if exist dist (rd /s /q dist)
if exist build (rd /s /q build)


echo Activating venv...
CALL .\venv\Scripts\activate.bat

echo Executing cxfreeze...
python setup.py build build_exe


if exist __pycache__ (rd /s /q __pycache__)

echo BUILD SUCCESSFUL!
