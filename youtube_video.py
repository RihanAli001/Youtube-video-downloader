import sys

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from pytube import YouTube


class window(QtWidgets.QMainWindow):
    def __init__(self):
        super(window, self).__init__()
        self.centralwid = QtWidgets.QWidget(self)
        self.vlayout = QtWidgets.QVBoxLayout()
        self.webview = QWebEngineView()
        self.webview.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webview.settings().setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        self.webview.page().fullScreenRequested.connect(lambda request: request.accept())
        url = "https://youtu.be/l6GroAW51Os"
        yt = YouTube(url)
        self.webview.setUrl(QUrl(f'https://www.youtube.com/embed/{yt.video_id}?rel=0'))
        self.vlayout.addWidget(self.webview)
        self.centralwid.setLayout(self.vlayout)
        self.setCentralWidget(self.centralwid)
        self.show()


app = QtWidgets.QApplication([])
ex = window()
sys.exit(app.exec_())
