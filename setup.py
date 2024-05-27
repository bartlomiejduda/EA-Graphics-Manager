import sys

from cx_Freeze import Executable, setup

from src.main import VERSION_NUM

base = None
if sys.platform == "win32":
    base = "Win32GUI"


executables = [
    Executable(
        "src/main.py",
        copyright="Copyright (C) 2024 Bartlomiej Duda",
        base=base,
        icon="src/data/img/ea_icon.ico",
        target_name="EA-Graphics-Manager-" + VERSION_NUM + ".exe",
    )
]

build_exe_options: dict = {
    "build_exe": "build_final/EA_Graphics_Manager",
    "packages": [],
    "includes": [],
    "excludes": [],
    "include_files": [],
}

options: dict = {"build_exe": build_exe_options}

setup(
    name="EA-Graphics-Manager " + VERSION_NUM,
    version=VERSION_NUM[1:],
    description="Tool for managing EA graphics",
    options=options,
    executables=executables,
)
