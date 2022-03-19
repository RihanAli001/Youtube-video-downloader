import os
import sys
import urllib.request
from Downloader import Ui_MainWindow
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, Qt, QPoint, QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QFileSystemModel, QShortcut
from pytube import YouTube, Search
import vlc

WINDOW_SIZE = 0


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.instance = vlc.Instance("prefer-insecure")
        self.media_player = self.instance.media_player_new()
        self.video_player_frame.setAutoFillBackground(True)
        self.video_position_slider.sliderMoved.connect(self.set_position)
        self.play_pause_btn.clicked.connect(self.play_pause)
        QShortcut(' ', self).activated.connect(self.play_pause)
        QShortcut('Ctrl+O', self).activated.connect(self.open_file)
        self.stop_btn.clicked.connect(self.stop)
        QShortcut('Alt+ ', self).activated.connect(self.play_pause)
        self.volume_slider.setValue(self.media_player.audio_get_volume())
        self.volume_slider.valueChanged.connect(self.set_volume)
        QShortcut('Up', self).activated.connect(self.update_volume_up)
        QShortcut('Down', self).activated.connect(self.update_volume_down)
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui)
        self.media = None
        self.isPaused = False

        self.webview = QWebEngineView(self.web_video_player_frame)
        self.verticalLayout_13.addWidget(self.webview)
        self.search_btn.clicked.connect(self.query_video_search)
        QShortcut('Ctrl+S', self).activated.connect(self.query_video_search)
        QShortcut('Ctrl+Shift+S', self).activated.connect(self.search_bar.setFocus)
        self.url_btn.clicked.connect(self.url_video_search)
        QShortcut('Ctrl+U', self).activated.connect(self.url_video_search)
        self.download_btn.clicked.connect(self.download_video)
        QShortcut('Ctrl+D', self).activated.connect(self.download_video)
        self.webview.urlChanged.connect(self.display_webview_url)

        self.model = QFileSystemModel()
        self.open_folder_btn.clicked.connect(self.open_folder)
        QShortcut('Ctrl+Shift+O', self).activated.connect(self.open_folder)
        self.tree_view_local.clicked.connect(self.set_file_to_player)

        self.old_pos = self.pos()
        self.option_btn.clicked.connect(self.menu_toggle)
        self.home_btn.clicked.connect(self.home_menu_page)
        self.local_btn.clicked.connect(self.local_menu_page)
        self.info_drop_down_btn.clicked.connect(self.info_drop_down)

        self.close_btn.clicked.connect(lambda: self.close())
        self.minimize_btn.clicked.connect(lambda: self.showMinimized())
        self.restore_btn.clicked.connect(lambda: self.restore_or_maximize_window())

    def display_webview_url(self):
        url = str(self.webview.url())
        url = url.replace("PyQt5.QtCore.QUrl('", "")
        url = url.replace("')", "")
        print(url)
        yt = YouTube(url)
        self.video_info_update(yt)

    def restore_or_maximize_window(self):
        global WINDOW_SIZE
        win_status = WINDOW_SIZE
        icon = QtGui.QIcon()
        if win_status == 0:
            WINDOW_SIZE = 1
            self.showMaximized()
            icon.addPixmap(QtGui.QPixmap(":/icons_white/icons_White/icon_restore.png"))
        else:
            WINDOW_SIZE = 0
            self.showNormal()
            icon.addPixmap(QtGui.QPixmap(":/icons_white/icons_White/icon_maximize.png"))
        self.restore_btn.setIcon(icon)

    def mouse_press_event(self, event):
        self.old_pos = event.globalPos()

    def mouse_move_event(self, event):
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def menu_toggle(self):
        if self.extra_left_space.width() == 0:
            self.extra_left_space.setMinimumWidth(300)
        else:
            self.extra_left_space.setMinimumWidth(0)

    def info_drop_down(self):
        icon = QtGui.QIcon()
        if self.video_info_frame.height() == 0:
            self.video_info_frame.setMaximumHeight(16777215)
            icon.addPixmap(QtGui.QPixmap(":/icons_white/icons_White/cil-arrow-bottom.png"))
        else:
            self.video_info_frame.setMaximumHeight(0)
            icon.addPixmap(QtGui.QPixmap(":/icons_white/icons_White/cil-arrow-top.png"))
        self.info_drop_down_btn.setIcon(icon)

    def home_menu_page(self):
        if self.stackedWidget.currentWidget() == self.home_page:
            self.menu_toggle()
        elif self.extra_left_space.width() == 0:
            self.menu_toggle()
        self.stackedWidget.setCurrentWidget(self.home_page)

    def local_menu_page(self):
        if self.stackedWidget.currentWidget() == self.local_page:
            self.menu_toggle()
        elif self.extra_left_space.width() == 0:
            self.menu_toggle()
        self.stackedWidget.setCurrentWidget(self.local_page)

    def play_pause(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_pause_btn.setText("Play")
            self.isPaused = True
        else:
            if self.media_player.play() == -1:
                self.open_file()
                return
            self.media_player.play()
            self.play_pause_btn.setText("Pause")
            self.timer.start()
            self.isPaused = False
            if self.video_player_frame.maximumHeight() == 0:
                self.web_video_player_frame.setMaximumHeight(0)
                self.video_player_frame.setMaximumHeight(16777215)

    def stop(self):
        self.media_player.stop()
        self.play_pause_btn.setText("Play")

    def show_yt_video_information(self):
        print(self.webview.title())

    def show_local_video_information(self):
        print(self.media.get_meta(0))

    def download_video(self):
        print("Downloading video with", self.download_video_quality.currentText(), "quality...")

    @staticmethod
    def is_internet():
        try:
            urllib.request.urlopen("http://youtube.com")
            return True
        except:
            print("Internet is not connected")
            return False

    def web_view_update(self):
        if self.media_player.is_playing():
            self.play_pause()
        if self.web_video_player_frame.maximumHeight() == 0:
            self.web_video_player_frame.setMaximumHeight(16777215)
            self.video_player_frame.setMaximumHeight(0)

    def url_video_search(self):
        if not self.is_internet():
            return
        url = self.search_bar.text()
        if not len(url):
            url = "https://youtu.be/Az-mGR-CehY"
        self.web_view_update()
        try:
            yt = YouTube(url)
        except:
            print("URL is not valid...")
            self.query_video_search()
            return
        self.web_update_video(yt)

    def query_video_search(self):
        if not self.is_internet():
            return
        query = self.search_bar.text()
        if not len(query):
            query = "RihanHack"
        self.web_view_update()
        try:
            s = Search(query)
        except:
            print("Query search error...")
            return
        print("Query Search:", query)
        yt = s.results[0]
        self.web_update_video(yt)

    def web_update_video(self, yt):
        self.webview.setUrl(QUrl(f'{yt.watch_url}?rel=0'))
        print(f'{yt.watch_url}?rel=0')
        self.video_info_update(yt)

    def video_info_update(self, yt):
        if yt.title != "":
            self.video_title_field.setText(yt.title)
            print("Video title " + yt.title + "...")
        if yt.description != "":
            self.video_description_field.setText(yt.description)
            print("Video description " + yt.description[:40] + "...")
        video_len = yt.length
        hours = int(video_len / (60 * 60))
        minutes = int((video_len - hours * 3600) / 60)
        seconds = video_len - hours * 3600 - minutes * 60
        self.video_length_field.setText(str(hours)+":"+str(minutes)+":"+str(seconds))
        print("Video length " + str(yt.length) + "...")
        if yt.author != "":
            self.video_author_field.setText(yt.author)
            print("Video author " + yt.author + "...")

    def open_file(self, filename=None):
        if filename is None:
            filename = QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))[0]
        if not filename:
            return

        # create the media
        if sys.version < '3':
            filename = vlc.unicode(filename)
        self.media = self.instance.media_new(filename)
        self.media_player.set_media(self.media)

        self.media.parse()
        # self.setWindowTitle(self.media.get_meta(0))
        self.top_bar_label.setText(self.media.get_meta(0) + " - YouTube Video Downloader")

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_player_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_player_frame.winId())
        elif sys.platform == "darwin":  # for macOS
            self.media_player.set_nsobject(int(self.video_player_frame.winId()))
        self.play_pause()
        self.show_local_video_information()

    def open_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.abspath('/home'))
        if not dir_path:
            return
        self.model.setRootPath(dir_path)
        self.tree_view_local.setModel(self.model)
        self.tree_view_local.setRootIndex(self.model.index(dir_path))
        self.tree_view_local.setColumnWidth(0, 250)

    def set_file_to_player(self):
        if not self.model.isDir(self.tree_view_local.currentIndex()):
            self.open_file(self.model.filePath(self.tree_view_local.currentIndex()))

    def set_volume(self, volume):
        self.media_player.audio_set_volume(volume)

    def update_volume_up(self):
        self.media_player.audio_set_volume(self.media_player.audio_get_volume() + 1)
        print(self.media_player.audio_get_volume())

    def update_volume_down(self):
        self.media_player.audio_set_volume(self.media_player.audio_get_volume() - 1)
        print(self.media_player.audio_get_volume())

    def set_position(self, position):
        try:
            self.media_player.set_position(position / 1000.0)
        finally:
            print("Position calculation error")

    def update_ui(self):
        try:
            self.video_position_slider.setValue(int(self.media_player.get_position() * 1000))
        finally:
            print("Slider position calculation error")

        if not self.media_player.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec_())
