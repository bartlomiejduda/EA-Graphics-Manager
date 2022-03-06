import sys
from cx_Freeze import setup, Executable
from src.main import VERSION_NUM

base = None
if sys.platform == "win32":
    base = "Win32GUI"


executables = [
    Executable(
        "src/main.py",
        copyright="Copyright (C) 2022 Bartlomiej Duda",
        base=base,
        icon="src/data/img/icon_bd.ico",
        target_name="EA-Graphics-Manager-" + VERSION_NUM + ".exe"
    )
]

build_exe_options: dict = {
    "packages": [],
    'includes': [],
    "excludes": [],
    'include_files': ['src/data/docs/readme.txt', 'LICENSE'],
}

options: dict = {
    'build_exe': build_exe_options
}

setup(
    name="EA-Graphics-Manager " + VERSION_NUM,
    version=VERSION_NUM[1:],
    description="Tool for managing EA graphics",
    options=options,
    executables=executables,
)
