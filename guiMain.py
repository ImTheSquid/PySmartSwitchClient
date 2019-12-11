import sys

from PyQt5.QtWidgets import QApplication, QWidget

from client import Client


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PySmartSwitch Client')

        self.show()


if __name__ == '__main__':
    Client()
    app = QApplication([])
    win = Main()
    sys.exit(app.exec_())
