from PyQt6 import QtCore, QtGui, QtWidgets
import time
import threading
import sys
import lib as song
import lib.libyt as libyt
import subprocess
import os
from mutagen import File
import zono.togglebool as toggle_bool
import widgets.progress
import sys
import pickle
from pathlib import Path
import PyTouchBar


pause_bar = False

with open('discord.pickle', 'wb') as file:
    pickle.dump(False, file)


class app:
    def run():
        app = QtWidgets.QApplication(['Audio'])
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec())


class Audio(QtCore.QObject):
    stopevent = QtCore.pyqtSignal()
    playevent = QtCore.pyqtSignal()
    nextevent = QtCore.pyqtSignal()

    def __init__(self, path):

        super().__init__()
        if path:
            self.playlist = song.playlist(path, end_event=self.end_signal)
        else:
            self.disabeled = True

        self.path = path

        self.playing_mode = False
        self.shuffling = False
        self.forwording = False

        self.current_song = None
        self.vol = 100
        self.clicked = True
        self.auto = toggle_bool.toggle_bool(True)
        self.close_thread = False
        self.stop_next = False
        self.paused = toggle_bool.toggle_bool(False)
        self.length_of_songs = len(self.playlist.songs)

    def end_signal(self, event):
        print('fffffffffffffff')
        if not self.auto.val:
            return

        self.nextevent.emit()

    def change_volume(self, volume):
        try:
            self.playlist.volume = volume
            self.current_song.mp3.audio_set_volume(volume)
        except:
            pass

    def get_song(self, elm):
        if elm == '':
            return 0
        Id = self.get_id(elm)
        if not Id:
            return False
        song = self.playlist.id_song_dict[Id]
        return song

    def update_path(self, path):
        del self.playlist
        self.playlist = song.playlist(path)
        self.length_of_songs = len(self.playlist.songs)
        self.stop()
        self.disabeled = False

    def __keep_pause__(self):
        self.current_song.paused = True
        time.sleep(0.5)
        self.current_song.paused = False

    def set_time(self, seconds):
        try:
            self.current_song.pause()
            self.paused.toggle()
        except:
            pass
        self.current_song.mp3.set_time(int(seconds) * 1000)
        time.sleep(0.01)
        try:
            self.current_song.pause()
            self.paused.toggle()
        except:
            pass

    def get_id(self, elm):
        find = list(elm)
        var_s = []
        try:
            while True:
                var_s.append(str(int(find.pop())))

        except:
            var_s.reverse()
            fin = ''.join(var_s)

        try:
            val = int(fin)
        except:
            val = False

        return val

    def pause(self):

        try:
            self.current_song.pause()
            self.paused.toggle()
        except:
            pass

    def stop(self):
        if self.current_song:
            self.current_song.stop()
        self.playlist.stop()
        self.current_song = None
        self.playlist.playing = False
        self.playing_mode = False
        self.forwording = False
        self.stopevent.emit()

    def get_song(self, elm):
        if elm == '':
            return 0

        Id = self.get_id(elm)
        if not Id:
            return 0
        song = self.playlist.id_song_dict[Id]
        self.playing = False
        return song

    def play(self, elm):
        if elm == '':
            return 0

        self.elm = elm
        self.stop()

        Id = self.get_id(elm)
        if not Id:
            return 0
        song = self.playlist.id_song_dict[Id]
        self.current_song = song
        self.curr_ID = Id

        song.play(self.vol)

        self.playevent.emit()

        self.playing_mode = True
        self.shuffling = False
        self.forwording = False

    def play_plus_1(self, elm):
        if elm == '':
            return 0
        self.stop()
        Id = self.get_id(elm)
        if Id + 1 > self.playlist.length_of_songs:
            Id = 0

        song = self.playlist.id_song_dict[Id + 1]
        self.current_song = song
        self.elm = f'id{Id+1}'
        self.curr_ID = Id

        song.play(self.vol)

        self.playevent.emit()

    def shuffle(self):
        self.stop()

        self.playlist.play()
        self.current_song = self.playlist.curr_song
        self.playing_mode = False
        self.shuffling = True
        self.forwording = False

        self.playevent.emit()

    def back(self):
        self.stop()
        self.playlist.play(mode='skip', state='back')
        self.current_song = self.playlist.curr_song

        self.playevent.emit()

    def forword(self):
        if self.shuffling:
            return self.shuffle()
        self.stop()
        self.playlist.play(mode='skip', state='forword')
        self.current_song = self.playlist.curr_song
        self.playing_mode = False
        self.shuffling = False
        self.forwording = True

        self.playevent.emit()


class YoutubeDownloader(QtCore.QObject):
    finished = QtCore.pyqtSignal(int, dict)
    progress = QtCore.pyqtSignal(dict)

    def __init__(self, url, ui, instance):
        super().__init__()
        self.url = url
        self.ui = ui
        self.instance = instance

    def run(self):
        code, i = libyt.download_mp3(
            self.url, self.instance.audio.playlist.path, lambda x: self.progress.emit(x))
        self.finished.emit(code, i)


class SongProgress(QtCore.QObject):
    updateevent = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            self.updateevent.emit()
            time.sleep(0.9)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(666, 650)
        self.MainWindow = MainWindow

        self.selected = ''

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.song_progress = QtWidgets.QSlider(self.centralwidget)
        self.song_progress.setGeometry(QtCore.QRect(130, 0, 431, 22))
        self.song_progress.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.song_progress.setObjectName("song_progress")
        self.song_progress.setRange(0, 100)
        self.play = QtWidgets.QPushButton(self.centralwidget)
        self.play.setGeometry(QtCore.QRect(260, 50, 93, 28))
        self.play.setObjectName("play")
        self.back = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(500, 60, 160, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setRange(0, 100)
        self.back.setGeometry(QtCore.QRect(169, 50, 91, 28))
        self.back.setObjectName("back")
        self.forword = QtWidgets.QPushButton(self.centralwidget)
        self.forword.setGeometry(QtCore.QRect(350, 50, 91, 28))
        self.length_widg = QtWidgets.QLabel(self.centralwidget)
        self.length_widg.setGeometry(QtCore.QRect(560, 0, 41, 16))
        self.length_widg.setObjectName("length_widg")
        self.name_song = QtWidgets.QLabel(self.centralwidget)
        self.name_song.setGeometry(QtCore.QRect(140, 20, 391, 20))
        self.name_song.setObjectName("name_song")
        self.time = QtWidgets.QLabel(self.centralwidget)
        self.time.setGeometry(QtCore.QRect(100, 0, 55, 16))

        self.time.setObjectName("time")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(450, 60, 55, 16))
        self.label_3.setObjectName("label_3")
        self.forword.setObjectName("forword")
        self.shuflle = QtWidgets.QPushButton(self.centralwidget)
        self.shuflle.setGeometry(QtCore.QRect(350, 80, 93, 28))
        self.shuflle.setObjectName("shuflle")
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setGeometry(QtCore.QRect(260, 80, 93, 28))
        self.stop.setObjectName("stop")
        self.pause = QtWidgets.QPushButton(self.centralwidget)
        self.pause.setGeometry(QtCore.QRect(170, 80, 93, 28))
        self.pause.setObjectName("pause")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(200, 120, 181, 22))
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(150, 120, 55, 16))
        self.label_2.setObjectName("label_2")
        self.musiclist = QtWidgets.QListWidget(self.centralwidget)
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(20, 40, 121, 121))
        self.graphicsView.setObjectName("graphicsView")
        self.musiclist.setGeometry(QtCore.QRect(20, 180, 621, 411))
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 30, 131, 101))
        self.label.setObjectName("label")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(450, 150, 151, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.musiclist.setObjectName("musiclist")
        MainWindow.setWindowIcon(QtGui.QIcon('icon.png'))
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 657, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")

        self.menuShortcuts = QtWidgets.QMenu(self.menubar)
        self.menuShortcuts.setObjectName("menuShortcuts")

        self.actionPause_space = QtGui.QAction(MainWindow)
        self.actionPause_space.setObjectName("actionPause_space")
        self.actionquit = QtGui.QAction(MainWindow)
        self.actionquit.setObjectName("actionquit")

        self.actionforword_ctrl_right = QtGui.QAction(MainWindow)
        self.actionforword_ctrl_right.setObjectName("actionforword_ctrl_right")
        self.actionback_ctrl_left = QtGui.QAction(MainWindow)
        self.actionback_ctrl_left.setObjectName("actionback_ctrl_left")
        self.actionshuffle_ctrl_s = QtGui.QAction(MainWindow)
        self.actionshuffle_ctrl_s.setObjectName("actionshuffle_ctrl_s")
        self.actionopen_new_folder_ctrl_o = QtGui.QAction(MainWindow)
        self.actionopen_new_folder_ctrl_o.setObjectName(
            "actionopen_new_folder_ctrl_o")

        self.number_songs = QtGui.QAction(MainWindow)
        self.number_songs.setObjectName("number_songs")

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpen)
        self.menubar.addAction(self.menuFile.menuAction())
        self.actionNotifications = QtGui.QAction(MainWindow)
        self.actionNotifications.setObjectName("actionNotifications")
        self.actionDiscord = QtGui.QAction(MainWindow)
        self.actionDiscord.setObjectName("actiondiscord")
        self.menuSettings.addAction(self.actionNotifications)
        self.menuSettings.addAction(self.actionDiscord)
        self.menuSettings.addAction(self.number_songs)

        self.clicked = False
        self.menuShortcuts.addAction(self.actionPause_space)
        self.menuShortcuts.addAction(self.actionforword_ctrl_right)
        self.menuShortcuts.addAction(self.actionback_ctrl_left)
        self.menuShortcuts.addAction(self.actionshuffle_ctrl_s)
        self.menuShortcuts.addAction(self.actionquit)
        self.menuShortcuts.addAction(self.actionopen_new_folder_ctrl_o)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(400, 150, 55, 16))
        self.label.setObjectName("label")

        self.action_yt_download = QtGui.QAction(MainWindow)
        self.action_yt_download.setObjectName("action_yt_download")

        self.menuYoutube = QtWidgets.QMenu(self.menubar)
        self.menuYoutube.setObjectName("menuYoutube")

        self.menuYoutube.addAction(self.action_yt_download)

        self.menubar.addAction(self.menuSettings.menuAction())

        self.menubar.addAction(self.menuShortcuts.menuAction())

        self.menubar.addAction(self.menuYoutube.menuAction())

        self.autoplay = QtWidgets.QCheckBox(self.centralwidget)
        self.autoplay.setGeometry(QtCore.QRect(450, 80, 81, 20))
        self.autoplay.setObjectName("autoplay")

        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.musiclist.setFont(font)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def get_path(self):
        home = Path.home()

        path = QtWidgets.QFileDialog.getExistingDirectory(self.MainWindow,
                                                          'Select Location of playlist',
                                                          str(home) + r'\music')

        return path

    def closeEvent(self, event):
        with open('shutdown.pickle', 'wb') as file:
            pickle.dump(True, file)
        os._exit(0)

    def update_path(self):
        home = Path.home()
        self.stop_()
        path = QtWidgets.QFileDialog.getExistingDirectory(self.MainWindow,
                                                          'Select Location of playlist',
                                                          str(home) + r'\music')
        if path:
            with open('path.pickle', 'wb') as file:
                pickle.dump(path, file)

            self.musiclist.clear()

            self.audio.update_path(path)

            self.number_songs.setText(f'{self.audio.length_of_songs} songs')

            self.refresh()

    def refresh_tools(self):
        global pause_bar
        while True:
            try:
                raw_seconds = self.audio.current_song.seconds
                song_length = self.audio.current_song.length

                elep = int(round(self.audio.current_song.elapsed_seconds(), 0))

                elapsed = elep

                perc = (elep / raw_seconds) * 100

                if elep > 59:
                    s = int(elep % 60)
                    if s <= 9:
                        s = f'0{s}'

                    m = int(elep / 60)

                    elep = f'{m}:{s}'

                if elapsed <= 9:
                    elep = f'0{elapsed}'

                if elapsed < 60:
                    elep = f'00:{elep}'

                self.length_widg.setText(song_length)

                if not pause_bar:
                    self.song_progress.setValue(int(perc))
                    self.time.setText(str(elep))

                time.sleep(0.85)
            except:
                time.sleep(1)
                pass

    def update_bar(self):
        raw_seconds = self.audio.current_song.seconds
        song_length = self.audio.current_song.length

        elep = int(round(self.audio.current_song.elapsed_seconds(), 0))

        elapsed = elep

        perc = (elep / raw_seconds) * 100

        if elep > 59:
            s = int(elep % 60)
            if s <= 9:
                s = f'0{s}'

            m = int(elep / 60)

            elep = f'{m}:{s}'

        if elapsed <= 9:
            elep = f'0{elapsed}'

        if elapsed < 60:
            elep = f'00:{elep}'

        self.length_widg.setText(song_length)

        if not pause_bar:
            self.song_progress.setValue(int(perc))
            self.time.setText(str(elep))

    def onclick(self, item):
        self.selected = item.text()

        song_int = self.audio.get_song(item.text())
        if not song_int:
            return 0

        file = File(song_int.path)
        artwork = file.tags.get('APIC:', file.tags.get('covr'))
        path = 'error.jfif'
        if artwork:
            artwork = artwork.data

            with open('image.jpg', 'wb') as img:
                img.write(artwork)
            path = 'image.jpg'

        pix = QtGui.QPixmap(path)
        smaller_pixmap = pix.scaled(119, 119, QtCore.Qt.AspectRatioMode.KeepAspectRatio.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.FastTransformation)
        item = QtWidgets.QGraphicsPixmapItem(smaller_pixmap)
        scene = QtWidgets.QGraphicsScene(self.MainWindow)
        scene.addItem(item)
        self.graphicsView.setScene(scene)

    def onselect(self, item):
        self.audio.play(item.text())

    def load_playlist(self):
        try:
            with open('path.pickle', 'rb') as file:
                path = pickle.load(file)

        except FileNotFoundError:
            msg = QtWidgets.QMessageBox(self.MainWindow)
            msg.setWindowTitle("No path")
            msg.setText(
                f"Pick a playlist directory")
            msg.exec()
            path = None
        if not path:
            path = self.get_path()
            if not path:
                msg = QtWidgets.QMessageBox(self.MainWindow)
                msg.setWindowTitle("No path")
                msg.setText("No path defined")
                msg.exec()

                os._exit(0)

            self.audio = Audio(path)
            with open('path.pickle', 'wb') as file:
                pickle.dump(path, file)
            return 0
        else:
            if not os.path.isdir(path):
                msg = QtWidgets.QMessageBox(self.MainWindow)
                msg.setWindowTitle("No path")
                msg.setText(
                    f"path {path} was moved or deleted please pick a new path")
                msg.exec()
                path = self.get_path()
                if not path:
                    msg = QtWidgets.QMessageBox(self.MainWindow)
                    msg.setWindowTitle("No path")
                    msg.setText("No path defined")
                    msg.exec()

                    os._exit(0)

                self.audio = Audio(path)
                with open('path.pickle', 'wb') as file:
                    pickle.dump(path, file)
                return 0

            self.audio = Audio(path)

    def refresh(self, List=None, ext_str=None):
        self.musiclist.clear()
        if ext_str:
            self.musiclist.addItem(ext_str)
            self.musiclist.addItem('')
        if List:
            for i in List:
                self.musiclist.addItem(i.get_info())
                self.musiclist.addItem('')
            return 0

        for i in self.audio.playlist.songs:
            self.musiclist.addItem(i.get_info())
            self.musiclist.addItem('')

    def play_(self):
        if not self.selected:
            return False
        self.audio.play(self.selected)
        return True

    def release_bar(self):
        global pause_bar
        self.audio.change_volume(self.audio.vol)
        pause_bar = False
        perc = int(self.song_progress.value())
        try:
            lenght = self.audio.current_song.seconds
        except:
            return -1

        perc /= 100
        perc *= lenght

        self.audio.set_time(perc)

    def discord_toggle(self):
        with open('settings.pickle', 'rb') as file:
            LOAD = pickle.load(file)

        if LOAD['discord']:
            LOAD['discord'] = False
            self.actionDiscord.setText('Discord Integration off')
        else:
            LOAD['discord'] = True
            self.actionDiscord.setText('Discord Integration on')
        with open('settings.pickle', 'wb') as file:
            pickle.dump(LOAD, file)

        msg = QtWidgets.QMessageBox(self.MainWindow)
        msg.setWindowTitle("Changes saved")
        msg.setText(
            "Changes saved please restart the app for your edits to take effect"
        )
        msg.exec()

    def click_bar(self):
        global pause_bar
        self.audio.change_volume(0)
        pause_bar = True

    def load_prefrances(self):
        with open('settings.pickle', 'rb') as file:
            settings = pickle.load(file)

        if settings['discord']:
            self.actionDiscord.setText('Discord Integration on')
            threading.Thread(target=self.discord_loop).start()
            threading.Thread(target=self.runner).start()

        else:
            self.actionDiscord.setText('Discord Integraton off')

    def stop_(self):
        self.song_progress.setSliderPosition(0)
        self.time.setText('00:00')
        self.length_widg.setText('00:00')
        self.name_song.setText('')
        self.audio.stop()
        path = 'error.jfif'
        pix = QtGui.QPixmap(path)
      

        smaller_pixmap = pix.scaled(119, 119, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.FastTransformation)
        item = QtWidgets.QGraphicsPixmapItem(smaller_pixmap)
        scene = QtWidgets.QGraphicsScene(self.MainWindow)
        scene.addItem(item)
        self.graphicsView.setScene(scene)

    def pause_(self):
        self.audio.pause()

    def back_(self):
        self.song_progress.setSliderPosition(0)

        if not self.clicked:
            song_ = self.audio.current_song
            if not song_:
                self.audio.back()
                self.ref_scene()
                self.clicked = False
                return 0
            self.audio.stop()
            self.audio.play(f'id{song_.id}')
            self.clicked = True
        else:
            song_ = self.audio.current_song
            ID = song_.id
            if ID < 1:
                ID = self.audio.playlist.length_of_songs
            self.audio.play(f'ID{song_.id-1}')
            self.ref_scene()
            self.clicked = False

    def discord_loop(self):
        while True:
            try:

                SONG_INFO = {
                    'name': self.audio.current_song.title,
                    'album': self.audio.current_song.album,
                    'artist': self.audio.current_song.artist,
                    'id': self.audio.current_song.id,
                    'last': self.audio.length_of_songs
                }

                with open('discord.pickle', 'wb') as file:
                    pickle.dump(SONG_INFO, file)

                time.sleep(14)
            except:
                SONG_INFO = {}

                with open('discord.pickle', 'wb') as file:
                    pickle.dump(SONG_INFO, file)
                time.sleep(14)

    def forword_(self):
        self.song_progress.setSliderPosition(0)
        if self.audio.shuffling:
            return self.audio.shuffle()
        try:
            ID = self.audio.current_song.id
            elem = f'ID{ID}'
            self.audio.stop()
            self.audio.play_plus_1(elem)
            self.ref_scene()
        except:
            self.audio.stop()
            self.audio.forword()
            self.ref_scene()

    def shuffle_(self):
        self.song_progress.setSliderPosition(0)
        self.audio.shuffle()
        self.ref_scene()

    def ref_scene(self, path=None):
        path = path or self.audio.current_song.path

        song_length = self.audio.current_song.length
        self.length_widg.setText(song_length)

        self.song_progress.setValue(0)
        self.time.setText('00:00')

        file = File(path)
        artwork = file.tags.get('APIC:', file.tags.get('covr'))
        path = 'error.jfif'
        if artwork:
            artwork = artwork.data

            with open('image.jpg', 'wb') as img:
                img.write(artwork)
            path = 'image.jpg'

        pix = QtGui.QPixmap(path)
        smaller_pixmap = pix.scaled(119, 119, QtCore.Qt.AspectRatioMode.KeepAspectRatio.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.FastTransformation)
        item = QtWidgets.QGraphicsPixmapItem(smaller_pixmap)
        scene = QtWidgets.QGraphicsScene(self.MainWindow)
        scene.addItem(item)
        self.graphicsView.setScene(scene)

        self.name_song.setText(
            f'{self.audio.current_song.title} by {self.audio.current_song.artist} from {self.audio.current_song.album}'
        )

    def _search_(self):

        term = self.lineEdit.text()
        term = term.strip()
        if not term:
            self.refresh()
            return 0

        if 'id:' in term:
            try:
                ID = self.audio.get_id(term)
                s = self.audio.playlist.search_playlist_id(ID)

            except:
                ID = term.replace('id:', '')
                self.musiclist.clear()
                self.musiclist.addItem(f'No songs with the id {ID}')
                return 0
        elif 'song_name:' in term:
            term = term.replace('song_name:', '')

            s = self.audio.playlist.search_playlist_song_name(term)
            if not s:
                self.musiclist.clear()
                self.musiclist.addItem(f'No songs with the name {term}')
        elif 'artist:' in term:
            term = term.replace('artist:', '')
            s = self.audio.playlist.search_playlist_artist(term)
            if not s:
                self.musiclist.clear()
                self.musiclist.addItem(f'No artist with the name {term}')
        elif 'album:' in term:
            term = term.replace('album:', '')

            s = self.audio.playlist.search_play_list_album(term)
            if not s:
                self.musiclist.clear()
                self.musiclist.addItem(
                    f'No results for album with the name {term}')

        else:
            s = self.audio.playlist.search_playlist(term)

        if s == []:

            self.musiclist.clear()
            self.musiclist.addItem(f'No results for search term {term}')
            return 0
        self.musiclist.addItem(f'{len(s)} results for {term}')
        self.musiclist.addItem('')

        self.refresh(List=s, ext_str=f'{len(s)} results for {term}')

    def quit_app(self):
        with open('shutdown.pickle', 'wb') as file:
            pickle.dump(True, file)
        self.audio.stop()
        os._exit(0)

    def download_song(self, e):
        text, ok = QtWidgets.QInputDialog.getText(
            self.MainWindow, 'Song url', 'Enter youtube url')

        if not ok:
            return

        Form = QtWidgets.QWidget()
        ui = widgets.progress.ProgressBar()
        ui.setupUi(Form)
        Form.show()

        self.thread = QtCore.QThread()
        self.worker = YoutubeDownloader(text, ui, self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)

        def refresh(status):
            ui.refresh(status)

        def finish(code, info):
            if code == 0:
                title = info['track'] or info['title']
                msg = QtWidgets.QMessageBox(self.MainWindow)
                msg.setWindowTitle(f"Downloaded {title}")
                msg.setText(
                    f"Succsesfully downloaded {title}")
                msg.exec()
                self.musiclist.clear()

                self.audio.update_path(self.audio.path)

                self.number_songs.setText(
                    f'{self.audio.length_of_songs} songs')

                self.refresh()
                return

            if code == -1:
                msg = QtWidgets.QMessageBox(self.MainWindow)
                msg.setWindowTitle(f"Error")
                msg.setText(
                    f"Unable to download invalid url")
                Form.hide()
                msg.exec()
                return

            if code == -2:
                msg = QtWidgets.QMessageBox(self.MainWindow)
                msg.setWindowTitle(f"Error")
                msg.setText(
                    f"Unable to download (cannot connect to the server check your internet connection or wait 5 minutes)")

                Form.hide()
                msg.exec()
                return

        self.worker.finished.connect(finish)
        self.worker.progress.connect(refresh)
        self.thread.start()

    def sort_by(self, act):
        if self.lineEdit.text():
            pass

        choice = self.comboBox.currentText()
        if choice == 'List':
            self.refresh()
        elif choice == 'Song length highest':
            order = self.audio.playlist.sort_by_low_song_length()
            self.refresh(List=order)
        elif choice == 'Song length lowest':
            order = self.audio.playlist.sort_by_high_song_length()
            self.refresh(List=order)

        elif choice == 'A-Z':
            order = self.audio.playlist.sort_by_a_z()
            self.refresh(List=order)

        elif choice == 'Z-A':
            order = self.audio.playlist.sort_by_z_a()
            self.refresh(List=order)

    def song_skip(self, ev):
        perc = int(ev)
        try:
            lenght = self.audio.current_song.seconds
        except:
            return -1

        perc /= 100
        perc *= lenght
        elep = int(perc)
        elapsed = perc

        if elep > 59:
            s = int(elep % 60)
            if s <= 9:
                s = f'0{s}'

            m = int(elep / 60)

            elep = f'{m}:{s}'

        if elapsed <= 9:
            elep = f'0{int(elapsed)}'

        if elapsed < 60:
            elep = f'00:{elep}'

        self.time.setText(str(elep))

    def runner(self):
        with open('discord.pickle', 'wb') as file:
            pickle.dump(False, file)

        with open('shutdown.pickle', 'wb') as file:
            pickle.dump(False, file)
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call(['discord_presence'], creationflags=CREATE_NO_WINDOW)

    def volume_changed(self, slot):
        self.audio.vol = self.horizontalSlider.value()
        self.audio.change_volume(self.audio.vol)

    def value_chaneged(self, slot):
        self.audio.skip_time(self.song_progress.value())

    def stop_event(self):
        self.song_timer.stop()

    def start_event(self):
        self.song_timer.start(900)
        self.ref_scene()

    def check_val_up(self, slot):
        self.audio.auto.toggle()
    
    def touchbar_play(self,x):
        if self.audio.current_song:
            if self.audio.paused.val:
                self.pause_()
                self.touchbar_play_btn.title = '⏸'
               
          
            else:
                self.pause_()
                self.touchbar_play_btn.title = '▶️'
        
        else:
            if self.play_():
                self.touchbar_play_btn.title = '⏸'

    def touchbar_playmode(self,func):
        self.touchbar_play_btn.title = '⏸'
        func()


    def touchbar_stop(self,x):
        self.stop_()
        self.touchbar_play_btn.title = '▶️'
        

    def init_touchbar(self):
        PyTouchBar.notify(None)
        space = PyTouchBar.TouchBarItems.Space.Flexible()
        space2 = PyTouchBar.TouchBarItems.Space.Large()
        self.touchbar_play_btn = PyTouchBar.TouchBarItems.Button(title='▶️',action=self.touchbar_play)
        btn2 = PyTouchBar.TouchBarItems.Button(title='⏩',action=lambda x:self.touchbar_playmode(self.forword_))
        btn3 = PyTouchBar.TouchBarItems.Button(title='⏪',action=lambda x:self.touchbar_playmode(self.back_))
        btn4 = PyTouchBar.TouchBarItems.Button(title='⏹',action=self.touchbar_stop)
        btn5 = PyTouchBar.TouchBarItems.Button(title='🔀',action=lambda x:self.touchbar_playmode(self.shuffle_))
        PyTouchBar.set_touchbar([space,btn3,self.touchbar_play_btn,btn2,space2,btn4,btn5,space])

    def end_event(self):
        if self.audio.shuffling:
            self.audio.shuffle()

        elif self.audio.playing_mode:
            self.audio.play_plus_1(self.audio.elm)

        elif self.audio.forwording:
            self.audio.forword()

        song_length = self.audio.current_song.length
        self.length_widg.setText(song_length)

        self.song_progress.setValue(0)
        self.time.setText('00:00')

        self.ref_scene()

    def retranslateUi(self, MainWindow):
        self.init_touchbar()
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        MainWindow.closeEvent = self.closeEvent
        self.name_song.setText(_translate("MainWindow", ""))
        self.time.setText(_translate("MainWindow", ""))
        self.play.setText(_translate("MainWindow", "Play"))
        self.autoplay.setText(_translate("MainWindow", "Autoplay"))
        self.autoplay.clicked.connect(self.check_val_up)
        self.autoplay.setChecked(True)
        self.play.clicked.connect(self.play_)
        self.lineEdit.textChanged.connect(self._search_)
        MainWindow.setWindowTitle('Audioplayer')
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open ctrl-o"))
        self.actionOpen.triggered.connect(self.update_path)

        self.shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+O"), MainWindow)
        self.shortcut.activated.connect(self.update_path)
        self.shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+S"), MainWindow)
        self.shortcut10 = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+P"), MainWindow)

        self.shortcut.activated.connect(self.shuffle_)
        self.label_3.setText(_translate("MainWindow", "volume"))
        self.label_2.setText(_translate("MainWindow", "Search:"))
        self.shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+Right"), MainWindow)
        self.actionquit.setText(_translate("MainWindow", "Quit app(ctrl q)"))
        self.actionquit.triggered.connect(self.quit_app)
        self.comboBox.activated.connect(self.sort_by)
        self.action_yt_download.triggered.connect(self.download_song)
        self.song_progress.sliderPressed.connect(self.click_bar)
        self.song_progress.sliderReleased.connect(self.release_bar)

        self.shortcut.activated.connect(self.forword_)
        self.horizontalSlider.setValue(100)

        self.shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+Left"), MainWindow)
        self.shortcut.activated.connect(self.back_)

        self.shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Alt+C"), MainWindow)
        self.shortcut.activated.connect(self.ref_scene)

        self.shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+Q"), MainWindow)
        self.shortcut.activated.connect(self.quit_app)

        self.shortcut = QtGui.QShortcut(
            QtGui.QKeySequence('Space'), MainWindow)
        self.shortcut.activated.connect(self.pause_)
        self.actionDiscord.triggered.connect(self.discord_toggle)

        self.song_progress.sliderMoved.connect(self.song_skip)

        self.musiclist.itemActivated.connect(self.onselect)
        self.musiclist.itemClicked.connect(self.onclick)
        self.back.setText(_translate("MainWindow", "<"))
        self.forword.setText(_translate("MainWindow", ">"))
        self.shuflle.setText(_translate("MainWindow", "Shuffle"))
        self.stop.setText(_translate("MainWindow", "Stop"))
        self.comboBox.setItemText(0, _translate("MainWindow", "List"))
        self.comboBox.setItemText(
            1, _translate("MainWindow", "Song length highest"))
        self.comboBox.setItemText(
            2, _translate("MainWindow", "Song length lowest"))

        self.comboBox.setItemText(
            3, _translate("MainWindow", "A-Z"))

        self.comboBox.setItemText(
            4, _translate("MainWindow", "Z-A"))
        self.label.setText(_translate("MainWindow", "Sort by:"))

        self.length_widg.setText(_translate("MainWindow", ""))
        self.stop.clicked.connect(self.stop_)
        self.action_yt_download.setText(
            _translate("MainWindow", "Download song"))
        self.song_timer = QtCore.QTimer()

        self.song_timer.timeout.connect(self.update_bar)
        self.forword.clicked.connect(self.forword_)
        self.back.clicked.connect(self.back_)
        self.pause.clicked.connect(self.pause_)
        self.shuflle.clicked.connect(self.shuffle_)
        self.pause.setText(_translate("MainWindow", "Pause"))
        self.menuShortcuts.setTitle(_translate("MainWindow", "Shortcuts"))
        self.horizontalSlider.sliderMoved.connect(self.volume_changed)
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuYoutube.setTitle(_translate("MainWindow", "Youtube"))
        self.actionNotifications.setText(
            _translate("MainWindow", "Notifications on"))
        self.actionDiscord.setText(
            _translate("MainWindow", "Discord integration on"))

        self.actionPause_space.setText('pause(space)')
        self.actionPause_space.triggered.connect(self.pause_)
        self.actionforword_ctrl_right.setText(
            _translate("MainWindow", "forword(ctrl right)"))
        self.actionback_ctrl_left.setText(
            _translate("MainWindow", "back(ctrl left)"))

        self.actionforword_ctrl_right.triggered.connect(self.forword_)
        self.actionback_ctrl_left.triggered.connect(self.back_)
        self.actionshuffle_ctrl_s.setText(
            _translate("MainWindow", "shuffle(ctrl-s)"))
        self.actionshuffle_ctrl_s.triggered.connect(self.shuffle_)

        self.actionopen_new_folder_ctrl_o.setText(
            _translate("MainWindow", "open new folder(ctrl-o)"))
        self.actionopen_new_folder_ctrl_o.triggered.connect(self.update_path)
        self.load_playlist()
        self.load_prefrances()

        self.number_songs.setText(
            _translate("MainWindow", f'{self.audio.length_of_songs} songs'))
        self.refresh()
        self.stop_()
        self.audio.stopevent.connect(self.stop_event)
        self.audio.playevent.connect(self.start_event)
        self.audio.nextevent.connect(self.end_event)


app.run()
