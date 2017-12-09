#creates m3u playlists
import utilities
import os

#creats a playlist from a directory
def playlist(path, playlistname, start='', end='', abspath=True, slash=os.sep):
    return playlistFromList(utilities.walkMusicFiles(path), playlistname, start, end, abspath, slash) #currently returns None, might change

#creates a playlist from a list of files
def playlistFromList(files, playlistname, start='', end='', abspath=True, slash=os.sep):
    with open(playlistname, 'a') as playlist:
        for song in files:
            if abspath:
                playlist.write(os.path.join(start,os.path.abspath(song),end).replace('\\', slash).replace('/', slash).rstrip(slash)+'\n')#stripping slashes in case end is an empty string
            else:
                playlist.write(ps.path.join(start,song,end).replace('\\', slash).replace('/', slash).rstrip(slash)+'\n')

if __name__ == '__main__':
    playlist('test files', 'test.m3u')
