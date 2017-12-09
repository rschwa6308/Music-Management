from mutagen.easyid3 import EasyID3


'''
key:
#f = filename
#a = album
#t = title
#r = artist
#n = track number
#d = date
'''
specials = {'#a' : 'album', '#t' : 'title', '#r' : 'artist', '#n' : 'tracknumber', '#d' : 'date'}

def edit(filename, key, value):
    songdata = EasyID3(filename)
    value = value.replace('#f', filename)
    for k, v in specials.items():
        try: value = value.replace(k, songdata[v])
        except KeyError: pass #if particular file does not have that metadata
    songdata[key] = value
    songdata.save()
        
