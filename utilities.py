import os

types = ['.mp3', '.wav', '.m4a', '.ogg', '.wma']

def walk(path):
    return (os.path.join(root, filename) for root, _, filenames in os.walk(path) for filename in filenames)

def walkMusicFiles(path):
    for fname in walk(path):
        if os.path.splitext(fname)[1] in types:
            yield fname
