from mutagen.easyid3 import EasyID3
import mutagen.id3

'''
key:
#f = filename
#a = album
#t = title
#r = artist
#n = track number
#d = date
'''
specials = {'#a': 'album', '#t': 'title', '#r': 'artist', '#n': 'tracknumber', '#d': 'date'}


def edit(filename, key, value):
    try:
        songdata = EasyID3(filename)
    except mutagen.id3.ID3NoHeaderError:
        songdata = mutagen.File(filename, easy=True)
        songdata.add_tags()
    value = value.replace('#f', filename)
    for k, v in specials.items():
        try:
            value = value.replace(k, songdata[v][0])
        except KeyError:
            value = value.replace(k, "")
    print(key + ": " + value)
    songdata[key] = value
    songdata.save()


if __name__ == '__main__':
    edit('test files\\2-01 Barbara Allen.mp3', 'title', '222#f')
