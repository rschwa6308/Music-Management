import os

types = ['.mp3', '.wav', '.m4a', '.ogg', '.wma', '.3gp', '.aac', '.aiff', '.flac', '.wma', '.webm', '.mp4'm '.flv', '.mov'] #not entirely comprehensive


def walk(path):
    return (os.path.join(root, filename) for root, _, filenames in os.walk(path) for filename in filenames)

def walkMusicFiles(path):
    for fname in walk(path):
        if os.path.splitext(fname)[1] in types:
            yield fname

def build_file_list(top, file_list=[]):
    for item in sorted(os.listdir(top), key=lambda x: x.split(".")[-1]):
        item = os.path.join(top, item)
        file_list.append(item)
        if os.path.isfile(item):
            pass
        else:
            file_list += build_file_list(item, file_list)
    return file_list
