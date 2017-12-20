import sys
from cx_Freeze import setup, Executable
import os
os.environ['TCL_LIBRARY'] = "D:\\Programming\\Python36\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "D:\\Programming\\Python36\\tcl\\tk8.6"

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter"],"includes":["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Music Manager",
        version = "0.1",
        description = "My GUI application!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Music Manager.py", base=base)])

##import sys  
##import cx_Freeze
##
##build_exe_options = {"include_files": [r'D:\Programming\code\Music-Management\tcl86t.dll', r"D:\Programming\code\Music-Management\tk86t.dll"],
##                     "includes":["tkinter"]}  
##
##base = None
##if sys.platform == "win32":
##    base = "Win32GUI"
##
##cx_Freeze.setup(  name = "guifoo",
##        version = "0.1",
##        description = "My GUI application!",
##        options = {"D:\\build_exe": build_exe_options},
##        executables = [cx_Freeze.Executable(r"D:\Programming\code\Music-Management\MusicManager.py", base=base)])
##setup(name="Name",  
##    version="1.0",  
##    description="Description",  
##    #options={"build_exe": build_exe_options},  
##    executables=[Executable(script=r"D:\Programming\code\Music-Management\Music Manager.py", base=base)],  
##    package_dir={'': ''},  
##    )  
