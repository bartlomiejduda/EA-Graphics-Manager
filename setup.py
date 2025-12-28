"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

import sys

from cx_Freeze import Executable, setup

from src.main import NIGHTLY_STR, VERSION_NUM

base = None
if sys.platform == "win32":
    base = "Win32GUI"

target_name: str = "EA-Graphics-Manager-" + VERSION_NUM + ("_" + NIGHTLY_STR if len(NIGHTLY_STR) > 0 else "") + ".exe"


executables = [
    Executable(
        "src/main.py",
        copyright="Copyright (C) 2024-2025 Bartlomiej Duda",
        base=base,
        icon="src/data/img/ea_icon.ico",
        target_name=target_name,
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
