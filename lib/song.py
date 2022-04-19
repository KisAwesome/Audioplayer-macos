import time
import zono.search as search
from mutagen.mp3 import MP3
from random import choice
from mutagen.id3 import ID3
import vlc
import os

# os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')


class song:
    ids = []

    def __init__(self, path, end_event=None):
        if not os.path.exists(path):
            raise FileNotFoundError
        self.mp3 = vlc.MediaPlayer(path)
        self.audio = MP3(path)
        self.elapsed_time = None

        self.ID3 = ID3(path)

        self.id = len(song.ids) + 1
        song.ids.append(self.id)
        self.paused = False
        self.tags = self.get_file_tags(path)
        self.title = self.tags[0]
        self.artist = self.tags[1]
        self.album = self.tags[2]

        self.tag_iter = list(self.tags)
        self.tag_iter.append(str(self.id))

        tags_ = []

        for i in self.tag_iter:
            tags_.append(str(i))

        self.keywords = tuple(tags_)

        if self.title == None:
            self.title = os.path.basename(path).replace('.mp3', '')

        self.playing = False

        self.seconds = self.audio.info.length
        length = self.audio.info.length
        minutes = int(length / 60)
        seconds = int(length % 60)
        self.length = f'{minutes}:{seconds}'
        if seconds <= 9:
            self.length = f'{minutes}:0{seconds}'

        filesize = round(os.stat(path).st_size / (1024 * 1024), 2)

        self.filesize = filesize
        self.filesize_form = f'{filesize}mb'

        self.path = path
        self.end_event = end_event
        if callable(self.end_event):
            events = self.mp3.event_manager()
            events.event_attach(
                vlc.EventType.MediaPlayerEndReached, self.end_event)

    def get_file_tags(self, f):

        mp3 = MP3(f)

        try:

            title = mp3['TIT2'][0]

        except:

            title = f.split('/')[-1][:-4]

        try:

            artist = mp3['TPE1'][0]

        except:

            artist = "Unknown"

        try:
            album = mp3['TALB'].text[0]

        except:

            album = None

        return (title, artist, album)

    def __repr__(self):
        return f'{self.title} by {self.artist} from {self.album} {self.length} long {self.filesize_form} id{self.id}'

    def get_info(self, Id=True):
        if not Id:
            return f'{self.title} by {self.artist} from {self.album} {self.length} long {self.filesize_form}'

        return f'{self.title} by {self.artist} from {self.album} {self.length} long {self.filesize_form} id{self.id}'

    def elapsed_seconds(self):
        try:
            s = self.mp3.get_time() / 1000
            return s
        except:
            return -1

    def play(self, volume=100):
        if self.isplaying():
            return -1

        self.playing = True
        self.paused = False
        self.mp3.stop()
        self.mp3.play()
        self.mp3.audio_set_volume(volume)

    def sync(self):
        while self.isplaying():
            print('f')
            time.sleep(0.1)

    def stop(self):
        self.playing = False
        self.paused = False
        self.mp3.stop()

    def pause(self):
        self.mp3.pause()
        if self.paused:
            self.paused = False
        else:
            self.paused = True

    def isplaying(self):
        return self.mp3.is_playing()


class playlist:
    shut = False

    def __init__(self, path, Print=True, end_event=None):
        r = os.listdir(path)
        self.playing = False
        self.print = Print
        self.path = path
        self.curr_song = None
        self.volume = 100
        self.songno = -1
        self.ids = []
        self.album_song_dict = {}
        self.keywords_song_dict = {}
        self.title_song_dict = {}
        self.artist_song_dict = {}
        self.songs = []
        self.current_playing = None
        self.id_song_dict = {}

        shut = False
        if not r:
            r = []
            shut = True

        if not shut:
            DICT = {}
            song.ids.clear()
            for i in r:
                if not '.mp3' in i:
                    continue

                ID = len(self.ids) + 1
                el = song(f'{path}/{i}', end_event)
                DICT[(el.title, el.id)] = 0
                self.artist_song_dict[(el.artist, el.id)] = el
                self.album_song_dict[(el.album, el.id)] = el
                self.id_song_dict[ID] = el
                self.songs.append(el)
                self.ids.append(ID)
                self.keywords_song_dict[el.keywords] = el
                self.title_song_dict[el.title] = el

        self.length_of_songs = len(self.songs)

    def search_playlist_id(self, idnumber):
        if idnumber in self.id_song_dict:
            return [self.id_song_dict[idnumber]]
        else:
            return []

    def search_playlist_artist(self, term):

        song_mathing_criteria = []
        for i in self.artist_song_dict:
            hold_search = search.search([str(i[0]).lower()])
            ans = hold_search.search(str(term.lower()))
            if ans:
                song_mathing_criteria.append(self.artist_song_dict[i])
        return song_mathing_criteria

    def search_play_list_album(self, term):
        song_matching_criteria = []
        for i in self.album_song_dict:
            hold_search = search.search([str(i[0]).lower()])
            ans = hold_search.search(str(term.lower()))

            if ans:
                song_matching_criteria.append(self.album_song_dict[i])

        return song_matching_criteria

    def sort_by_high_song_length(self):
        def take_first(elem):
            return elem[0]
        new = []

        for song in self.songs:
            new.append((song.seconds, song.id))

        new.sort(key=take_first)

        fin = []

        for elem in new:
            fin.append(self.id_song_dict[elem[1]])

        return fin

    def sort_by_low_song_length(self):
        def take_first(elem):
            return elem[0]
        new = []

        for song in self.songs:
            new.append((song.seconds, song.id))

        new.sort(key=take_first, reverse=True)

        fin = []

        for elem in new:
            fin.append(self.id_song_dict[elem[1]])

        return fin

    def search_playlist_song_name(self, song_name):
        songs_matching_criteria = []
        for i in self.title_song_dict:
            hold_search = search.search([str(i).lower().strip()])
            ans = hold_search.search(str(song_name).lower().strip())

            if ans:
                songs_matching_criteria.append(self.title_song_dict[i])
        return songs_matching_criteria

    def search_playlist(self, term):
        songs_matching_criteria = []
        for i in self.keywords_song_dict:
            hold_search = search.search(i)
            ans = hold_search.search(term.lower())

            if ans:
                songs_matching_criteria.append(self.keywords_song_dict[i])

        return songs_matching_criteria

    def play(self, internal=False, mode='shuffle', state='forword'):
        global song

        if self.playing:
            return -1

        self.playing = True
        if mode == 'shuffle':
            song_ = choice(self.songs)
        elif mode == 'skip':
            if state == 'back':
                if self.songno < 0:
                    self.songs[0].play(self.volume)
                    self.songno += 1
                    self.curr_song = self.songs[0]
                    return 0

                current_song = self.songs[self.songno - 1]
                self.songno -= 1
                self.curr_song = current_song
                current_song.play(self.volume)
                return 0
            elif state == 'forword':
                if self.songno + 1 > len(self.songs):
                    return 0
                current_song = self.songs[self.songno + 1]

                self.songno += 1

                current_song.play(self.volume)

                self.curr_song = current_song

                return 0

        self.curr_song = song_
        song_.play(self.volume)
        time.sleep(0.09)

    def stop(self):
        self.playing = False
        if self.curr_song:
            self.curr_song.stop()
