
:: BAT script for making exe file
:: Created on 01.03.2022 by Bartlomiej Duda


@ECHO OFF
if exist dist (rd /s /q dist)
if exist build (rd /s /q build)
if exist build_final (rd /s /q build_final)


echo Activating venv...
CALL .\venv\Scripts\activate.bat

echo Executing cxfreeze...
python setup.py build build_exe


if exist __pycache__ (rd /s /q __pycache__)

echo Copying files...
set BUILD_PATH=.\build_final\EA-Graphics-Manager
copy .\src\data\docs\readme.txt %BUILD_PATH%\readme.txt
copy .\LICENSE %BUILD_PATH%\LICENSE
mkdir %BUILD_PATH%\src\data\img
copy .\src\data\img\ea_icon.ico %BUILD_PATH%\src\data\img\ea_icon.ico


echo BUILD SUCCESSFUL!
