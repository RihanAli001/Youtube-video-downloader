import os
import sys
import urllib.request
import threading
from Downloader import Ui_MainWindow
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QFileSystemModel, QShortcut
from pytube import YouTube, Search
import vlc

WINDOW_SIZE = 0


class MyMainWindow(QMainWindow, Ui_MainWindow):
    """
    Initialization function
    """

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.top_bar.hide()

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
        self.yt = None

        self.model = QFileSystemModel()
        self.open_folder_btn.clicked.connect(self.open_folder)
        QShortcut('Ctrl+Shift+O', self).activated.connect(self.open_folder)
        self.tree_view_local.clicked.connect(self.set_file_to_player)

        self.old_pos = self.pos()
        self.option_btn.clicked.connect(self.menu_toggle)
        self.home_btn.clicked.connect(self.set_main_home_page)
        self.local_btn.clicked.connect(self.set_main_local_page)
        self.info_drop_down_btn.clicked.connect(self.info_drop_down)

        self.close_btn.clicked.connect(lambda: self.close())
        self.minimize_btn.clicked.connect(lambda: self.showMinimized())
        self.restore_btn.clicked.connect(lambda: self.restore_or_maximize_window())

        self.short_msg_notification("Ready to go...")

    """
    Showing short process message to user
    """

    def short_msg_notification(self, msg):
        self.short_msg_label.setText(msg)

    """
    Searching youtube video using video Url.
    """

    def url_video_search(self):
        if not self.is_internet():
            return
        url = self.search_bar.text()
        if not len(url):
            url = "https://youtu.be/Az-mGR-CehY"
        self.set_main_home_page()
        try:
            self.yt = YouTube(url, on_progress_callback=self.download_callback)
        except Exception as e:
            print("URL is not valid...\n", e)
            self.short_msg_notification("URL is not valid...")
            self.query_video_search()
            return
        self.web_update_video()

    """
    Searching youtube video using search query.
    """

    def query_video_search(self):
        if not self.is_internet():
            return
        query = self.search_bar.text()
        if not len(query):
            query = "Rihan Ali001"
        self.set_main_home_page()
        try:
            s = Search(query)
        except Exception as e:
            print("Query search error...\n", e)
            self.short_msg_notification("Something went wrong...")
            return
        print("Query Search:", query)
        self.yt = s.results[0]
        self.web_update_video()

    """
    Checking internet connection for playing youtube videos.
    """

    def is_internet(self):
        try:
            urllib.request.urlopen("http://youtube.com")
            return True
        except Exception as e:
            print("Internet is not connected\n", e)
            self.short_msg_notification("Internet is not connected...")
            return False

    """
    Updating home page for new video Url.
    """

    def web_update_video(self):
        self.webview.setUrl(QUrl(f'{self.yt.watch_url}?rel=0'))
        print(f'{self.yt.watch_url}?rel=0')

    """
    Displaying youtube video url
    """

    def display_webview_url(self, url):
        url = str(url).replace("PyQt5.QtCore.QUrl('", "")
        url = url.replace("')", "")
        print(url)
        self.yt = YouTube(url, on_progress_callback=self.download_callback)
        self.update_video_qualities()
        # threading.Thread(target=self.update_video_qualities, args=()).start()
        self.video_info_update()

    """
    Give video quality options to user for downloading video
    """

    def update_video_qualities(self):
        self.download_video_quality.clear()
        print("Option box is cleared...")
        stream = self.yt.streams.filter(progressive=True)
        if not len(stream):
            print(len(stream))
            self.download_video_quality.addItems("--no quality--")
            print("No quality found...")
            return
        print(stream)
        for i in stream:
            self.download_video_quality.addItem(i.resolution)
            print("Quality :", i.resolution)

    def download_callback(self, stream, chunk, bytes_remaining):
        file_size = stream.filesize
        bytes_downloaded = file_size - bytes_remaining
        print(chunk)
        self.short_msg_notification(f"{bytes_downloaded}/{file_size} Downloading...")
        if bytes_downloaded == file_size:
            self.short_msg_notification(f"{bytes_downloaded}/{file_size} Downloaded")

    """
    Downloading youtube video with selected video resolution.
    """

    def download_video(self):
        self.short_msg_notification("Wait, downloading...")
        threading.Thread(target=self.download, args=()).start()

    def download(self):
        quality = self.download_video_quality.currentText()
        print(quality)
        self.yt.streams.filter(progressive=True, res=quality).first().download()
        self.short_msg_notification("Download done...")

    """"
    Youtube video information update in video information section
    """

    def video_info_update(self):
        if self.yt.title != "":
            self.video_title_field.setText(self.yt.title)
            print("Video title " + self.yt.title + "...")
        if self.yt.description != "":
            self.video_description_field.setText(self.yt.description)
            print("Video description " + self.yt.description[:40] + "...")
        video_len = self.yt.length
        hours = int(video_len / (60 * 60))
        minutes = int((video_len - hours * 3600) / 60)
        seconds = video_len - hours * 3600 - minutes * 60
        self.video_length_field.setText(str(hours) + ":" + str(minutes) + ":" + str(seconds))
        print("Video length " + str(self.yt.length) + "...")
        if self.yt.author != "":
            self.video_author_field.setText(self.yt.author)
            print("Video author " + self.yt.author + "...")

    """
    Restore or maximizing the window
    """

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

    """
    Show/hide left navigation bar.
    """

    def menu_toggle(self):
        if self.left_nav.minimumWidth() == 0:
            self.left_nav.setMinimumWidth(60)
            self.left_nav.setMaximumWidth(60)
        else:
            self.left_nav.setMinimumWidth(0)
            self.left_nav.setMaximumWidth(0)

    """
    Showing main home page (Youtube website page) and hide media player page to the user.
    """

    def set_main_home_page(self):
        if self.media_player.is_playing():
            self.play_pause()

        if self.extra_left_space.minimumWidth() != 0:
            self.extra_left_space.setMinimumWidth(0)

        if self.main_stacked_pages.currentWidget() == self.main_local_page:
            self.main_stacked_pages.setCurrentWidget(self.main_home_page)

    """
    Showing main local page (media player page) and hide main home page to user.
    """

    def set_main_local_page(self):
        if self.main_stacked_pages.currentWidget() == self.main_home_page:
            self.main_stacked_pages.setCurrentWidget(self.main_local_page)
        elif self.extra_left_space.minimumWidth() == 0:
            self.extra_left_space.setMinimumWidth(300)
        else:
            self.extra_left_space.setMinimumWidth(0)

    """
    Show/hide video information page to the user.
    """

    def info_drop_down(self):
        icon = QtGui.QIcon()
        if self.video_info_frame.height() == 0:
            self.video_info_frame.setMaximumHeight(16777215)
            icon.addPixmap(QtGui.QPixmap(":/icons_white/icons_White/cil-arrow-bottom.png"))
        else:
            self.video_info_frame.setMaximumHeight(0)
            icon.addPixmap(QtGui.QPixmap(":/icons_white/icons_White/cil-arrow-top.png"))
        self.info_drop_down_btn.setIcon(icon)

    """
    Showing youtube video information.
    """

    def show_yt_video_information(self):
        print(self.webview.title())

    """
    Showing media player video information.
    """

    def show_local_video_information(self):
        print(self.media.get_meta(0))

    """
    Play/pause the media player if player has no media then open file
    """

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
            if self.main_stacked_pages.currentWidget() == self.main_home_page:
                self.main_stacked_pages.setCurrentWidget(self.main_local_page)

    """
    Stop media player.
    """

    def stop(self):
        self.media_player.stop()
        self.play_pause_btn.setText("Play")

    """"
    Open file and set file to media player.
    """

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
        self.setWindowTitle("YouTube Video Downloader - " + self.media.get_meta(0))
        self.top_bar_label.setText(self.media.get_meta(0) + " - YouTube Video Downloader")

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_player_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_player_frame.winId())
        elif sys.platform == "darwin":  # for macOS
            self.media_player.set_nsobject(int(self.video_player_frame.winId()))
        self.play_pause()
        self.show_local_video_information()

    """
    Open folder for displaying videos in navigation section.
    """

    def open_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.abspath('/home'))
        if not dir_path:
            return
        self.model.setRootPath(dir_path)
        self.tree_view_local.setModel(self.model)
        self.tree_view_local.setRootIndex(self.model.index(dir_path))
        self.tree_view_local.setColumnWidth(0, 250)

    """
    Set file to media player from local navigation section.
    """

    def set_file_to_player(self):
        if not self.model.isDir(self.tree_view_local.currentIndex()):
            self.open_file(self.model.filePath(self.tree_view_local.currentIndex()))

    """
    Set media player volume.
    """

    def set_volume(self, volume):
        self.media_player.audio_set_volume(volume)

    """
    Increase the media player volume.
    """

    def update_volume_up(self):
        self.media_player.audio_set_volume(self.media_player.audio_get_volume() + 1)
        print(self.media_player.audio_get_volume())

    """
    Decrease the media player volume.
    """

    def update_volume_down(self):
        self.media_player.audio_set_volume(self.media_player.audio_get_volume() - 1)
        print(self.media_player.audio_get_volume())

    """
    Set media player slider position.
    """

    def set_position(self, position):
        try:
            self.media_player.set_position(position / 1000.0)
        finally:
            print("Position calculation error")

    """
    Update media player Ui when it is playing.
    """

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
