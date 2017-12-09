import os
import utilities

def filestructure(path):
    for f in utilities.walk(path):
        dirs = list(reversed(list(splitpath(f))))
        folders = list(getfolders(path))
        dirs = [x for x in dirs if x not in folders]
        newdir = os.path.abspath(os.path.join(path, *dirs))
        if not os.path.isdir(os.path.dirname(newdir)):
            os.mkdir(os.path.dirname(newdir))
        if f != newdir:
            os.rename(f, newdir)
    #remove the now empty folders
    for folder in reversed(utilities.build_file_list(path)):
        if os.path.isdir(folder):
            if not os.listdir(folder):
                os.rmdir(folder)

#identify empty folders
def getfolders(path):
    empty = True
    for entry in os.listdir(path):
        entry = os.path.join(path, entry)
        if os.path.isfile(entry):
            empty = False
        elif os.path.isdir(entry):
            yield from getfolders(entry)
    if empty:
        yield os.path.basename(path)
    
#gets every directory along the path, but in reverse order
def splitpath(root):
    path, end = os.path.split(root)
    yield end
    if path != '':
        yield from splitpath(path)


'''
identify and remove empty folders (folders with no files, only subfolders
'''
if __name__ == '__main__':
    filestructure('test folders')
