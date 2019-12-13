import json
import socket
import sys
from os import makedirs
from os.path import join, isdir

import appdirs
from PyQt5 import QtCore
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QGroupBox, QVBoxLayout, QListWidget, QPushButton, QLabel, QLineEdit, \
    QSpinBox

"""
This class handles client-server communication including opening/closing connections using GUI's
"""

PORT = 30000


class Client:
    def __init__(self, parent):
        self.parent = parent
        ConnectionSplash(parent)
        return
        # Testing code
        HOST = input('Enter destination IP:')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
            except (ConnectionRefusedError, OSError):
                print('ERROR: Connection refused or client does not exist. Exiting...')
                return
            s.sendall(b'Hello, World!')
            data = s.recv(1024)

        print('Received: ' + repr(data))


class ConnectionSplash(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('New Connection')
        # Keep focus on window
        self.setModal(True)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.loaded_connections = self.load_profiles()

        main_layout = QHBoxLayout()

        # Saved IP's
        saved_box = QGroupBox('Saved')
        saved_layout = QVBoxLayout()
        saved_box.setLayout(saved_layout)
        self.save_list = QListWidget()
        self.save_list.addItem('New Connection...')
        saved_layout.addWidget(self.save_list)
        self.remove_item = QPushButton('Remove Item')
        self.remove_item.setEnabled(False)
        saved_layout.addWidget(self.remove_item)

        # Connection
        connect_box = QGroupBox('Connection Details')
        connect_layout = QVBoxLayout()
        connect_box.setLayout(connect_layout)

        connection_options = QHBoxLayout()

        # Connection details
        host_label = QLabel('Server IP:')
        connect_layout.addWidget(host_label)
        self.address = QLineEdit()
        self.address.textChanged.connect(self.check_arguments)
        connect_layout.addWidget(self.address)
        port_label = QLabel('Port:')
        connect_layout.addWidget(port_label)
        self.port = QSpinBox()
        self.port.setMinimum(0)
        self.port.setMaximum(65536)
        self.port.setValue(30000)
        connect_layout.addWidget(self.port)
        pass_label = QLabel('Password:')
        connect_layout.addWidget(pass_label)
        self.password = QLineEdit()
        self.password.textChanged.connect(self.check_arguments)
        self.password.setEchoMode(QLineEdit.Password)
        connect_layout.addWidget(self.password)
        connect_layout.addStretch()

        # Buttons to control connection
        self.connect = QPushButton('Connect')
        self.connect.setEnabled(False)
        self.save = QPushButton('Save')
        self.save.setEnabled(False)
        connection_options.addWidget(self.save)
        connection_options.addStretch()
        connection_options.addWidget(self.connect)
        connect_layout.addStretch()
        connect_layout.addLayout(connection_options)

        main_layout.addWidget(saved_box)
        main_layout.addWidget(connect_box)
        self.setLayout(main_layout)
        self.show()

    def load_profiles(self):
        user_dir = appdirs.user_data_dir('PySmartSwitchClient', 'JackHogan')
        if not isdir(user_dir):
            makedirs(user_dir, exist_ok=True)
        open(join(user_dir, 'profiles.txt'), 'w+')
        with open(join(user_dir, 'profiles.txt'), 'r') as json_file:
            if len(json_file.readlines()) == 0:
                with open(join(user_dir, 'profiles.txt'), 'w') as writer:
                    writer.write('{}')
                    writer.close()
            profiles = json.load(json_file)
            for profile in profiles:
                self.save_list.addItem(profile)
        return profiles

    def closeEvent(self, event: QCloseEvent):
        sys.exit(0)

    # Checks to make sure that all parameters are filled before allowing save/connection
    def check_arguments(self):
        ok = len(self.password.text()) > 0 and len(self.address.text()) > 0
        self.save.setEnabled(ok)
        self.connect.setEnabled(ok)

    def save_connection(self):
        pass
