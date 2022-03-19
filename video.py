import sys
import os.path
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QSlider, QHBoxLayout, QPushButton, \
    QVBoxLayout, QAction, QFileDialog, QApplication
import vlc


class Player(QMainWindow):
    def __init__(self, master=None):
        QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.media_player = self.instance.media_player_new()

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin":  # for macOS
            from PyQt5.QtWidgets import QMacCocoaViewContainer
            self.video_frame = QMacCocoaViewContainer(0)
        else:
            self.video_frame = QFrame()
        self.palette = self.video_frame.palette()
        self.palette.setColor(QPalette.Window,
                              QColor(0, 0, 0))
        self.video_frame.setPalette(self.palette)
        self.video_frame.setAutoFillBackground(True)
        self.media = None

        self.position_slider = QSlider(Qt.Horizontal, self)
        self.position_slider.setToolTip("Position")
        self.position_slider.setMaximum(1000)
        self.position_slider.sliderMoved.connect(self.set_position)

        self.h_button_box = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.h_button_box.addWidget(self.play_button)
        self.play_button.clicked.connect(self.play_pause)

        self.stop_button = QPushButton("Stop")
        self.h_button_box.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop)

        self.h_button_box.addStretch(1)
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.media_player.audio_get_volume())
        self.volume_slider.setToolTip("Volume")
        self.h_button_box.addWidget(self.volume_slider)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.v_box_layout = QVBoxLayout()
        self.v_box_layout.addWidget(self.video_frame)
        self.v_box_layout.addWidget(self.position_slider)
        self.v_box_layout.addLayout(self.h_button_box)

        self.widget.setLayout(self.v_box_layout)

        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.open_file)
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(sys.exit)
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui)
        self.isPaused = False

    def play_pause(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText("Play")
            self.isPaused = True
        else:
            if self.media_player.play() == -1:
                self.open_file()
                return
            self.media_player.play()
            self.play_button.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def stop(self):
        self.media_player.stop()
        self.play_button.setText("Play")

    def open_file(self, filename=None):
        if filename is None:
            filename = QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))[0]
        if not filename:
            return

        # create the media
        if sys.version < '3':
            filename = vlc.unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.media_player.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in its own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":  # for macOS
            self.media_player.set_nsobject(int(self.video_frame.winId()))
        self.play_pause()

    def set_volume(self, volume):
        self.media_player.audio_set_volume(volume)

    def set_position(self, position):
        # setting the position to where the slider was dragged
        self.media_player.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def update_ui(self):
        # setting the slider to the desired position
        self.position_slider.setValue(self.media_player.get_position() * 1000)

        if not self.media_player.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 480)
    if sys.argv[1:]:
        player.open_file(sys.argv[1])
    sys.exit(app.exec_())
