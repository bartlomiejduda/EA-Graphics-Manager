
:: BAT script for making exe file
:: Created on 01.03.2022 by Bartlomiej Duda

:: Execute this from Python virtualenv

if exist dist (rd /s /q  dist)


.\venv\Scripts\python.exe -m cxfreeze -c main.py --target-dir dist


if exist  __pycache__ (rd /s /q  __pycache__)
