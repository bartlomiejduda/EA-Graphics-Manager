# import sys
from cx_Freeze import setup, Executable
from main import VERSION_NUM

build_options = {"packages": [], "excludes": []}

# base = None
# if sys.platform == "win32":
#     base = "Win32GUI"
base = "Console"

executables = [Executable("main.py", base=base, target_name="EA-Graphics-Manager-" + VERSION_NUM + ".exe")]

setup(
    name="EA-Graphics-Manager " + VERSION_NUM,
    version=VERSION_NUM,
    description="Tool for managing EA graphics",
    options={"build_exe": build_options},
    executables=executables,
)
