import urllib.request


class YoutubeFun:
    @staticmethod
    def is_internet():
        try:
            urllib.request.urlopen("http://youtube.com")
            return True
        except Exception as e:
            print("Internet is not connected\n", e)
            return False


if __name__ == '__main__':
    win = YoutubeFun()
    if win.is_internet():
        print("Internet is connected...")
