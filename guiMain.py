import sys

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QTextEdit, \
    QLineEdit, QPushButton

from client import Client


class Main(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('PySmartSwitch Client')

        main_layout = QHBoxLayout()

        # Layout for connection, power status
        status_layout = QVBoxLayout()
        toggle_box = QGroupBox('Power Status')
        toggle_box.setFixedSize(QSize(200, 200))
        status_layout.addWidget(toggle_box)
        status_box = QGroupBox('Connection Status')
        stat_box_layout = QVBoxLayout()
        status_box.setLayout(stat_box_layout)
        status_box.setFixedWidth(200)
        status_layout.addWidget(status_box)
        self.connection_status = QTextEdit()
        self.connection_status.setReadOnly(True)
        stat_box_layout.addWidget(self.connection_status)

        log_box = QGroupBox('Log')
        log_layout = QVBoxLayout()
        log_box.setLayout(log_layout)
        self.connection_log = QTextEdit()
        self.connection_log.setReadOnly(True)
        log_layout.addWidget(self.connection_log)
        send_command_layout = QHBoxLayout()
        log_layout.addLayout(send_command_layout)
        self.command_sender = QLineEdit()
        self.command_sender.setPlaceholderText('Enter command')
        self.command_sender.textChanged.connect(self.update_command_send)
        send_command_layout.addWidget(self.command_sender)
        self.send_command_button = QPushButton('Send')
        self.send_command_button.clicked.connect(self.send_command)
        self.send_command_button.setEnabled(False)
        send_command_layout.addWidget(self.send_command_button)

        main_layout.addLayout(status_layout)
        main_layout.addWidget(log_box)

        self.setLayout(main_layout)
        self.show()

        Client(self)

    def update_command_send(self):
        self.send_command_button.setEnabled(len(self.command_sender.text()) > 0)

    def send_command(self):
        self.command_sender.setText('')

    def keyPressEvent(self, event: QKeyEvent):
        # Track Enter key
        if event.key() == 16777220 and len(self.command_sender.text()) > 0:
            self.send_command()


if __name__ == '__main__':
    app = QApplication([])
    win = Main()
    sys.exit(app.exec_())
