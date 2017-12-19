import Helpers.utilities as utilities
from mutagen.easyid3 import EasyID3
import os
'''
A generator
Takes a list of dictionary keys for the mutagen.File dictionary
'''


def search(term, keys, path):
    for key in keys:
        yield from searchHelper(term, key, path)


def searchHelper(term, key, path):
    term = term.lower()
    for f in utilities.walkMusicFiles(path):
        if key == 'filename':
            if term in f.lower():
                yield f
        else:
            if os.path.splitext(f)[1] == '.mp3':
                songdata = EasyID3(f)
                if key in songdata.keys() and len(list(filter(lambda x : term in x.lower(), songdata[key]))): #this could be a bit shorter using lists instead of filter
                    yield f
                

if __name__ == '__main__':
    for result in search('a', ['title'], 'test files'):
        print(result)
