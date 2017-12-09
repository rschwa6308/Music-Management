import os
import utilities
from utilities import types
import subprocess

commandline = lambda x : subprocess.call(x, shell=True)

#might need to use absolute file paths
def convert(path, ext):
    command = 'ffmpeg -i "{path}{oldext}" "{path}{newext}"' #assumes ffmpeg is in the users's path'
    def getCommand(fname):
        name, oldext = os.path.splitext(fname)
        return command.format(path=name, oldext=oldext, newext=ext)
    if os.path.isfile(path):
        if not os.path.isfile(os.path.splitext(path)[0] + ext):
            commandline(getCommand(path))
    else:
        for f in utilities.walkMusicFiles(path):
            if not os.path.isfile(os.path.splitext(path)[0] + ext):
                commandline(getCommand(f))
        


if __name__ == "__main__":
    convert('test files', '.wav')
    #test stuff
