import json
import socket
import sys
from os import makedirs, remove
from os.path import join, isdir, isfile

import appdirs
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QGroupBox, QVBoxLayout, QListWidget, QPushButton, QLabel, QLineEdit, \
    QSpinBox, QInputDialog, QMessageBox, QAbstractItemView
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization as serial, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

"""
This class handles client-server communication including opening/closing connections using GUI's
"""


class Client:
    def __init__(self, parent):
        self.parent = parent

        # Generate keys
        print('Generating key pair...')
        self.private_key = rsa.generate_private_key(65537, 2048, default_backend())
        self.public_key = self.private_key.public_key()
        self.server_key = None
        print('Finished generating keys.')

        self.try_connection()

    def try_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            failed = True
            while failed:
                c = ConnectionSplash(self.parent)
                HOST = c.get_address()
                PORT = c.get_port()

                try:
                    failed = False
                    s.connect((HOST, PORT))
                except (ConnectionRefusedError, OSError):
                    failed = True
                    QMessageBox.critical(self.parent, 'Connection Error',
                                         'Connection failed. Host refused connection or '
                                         'does not exist.')
            s.sendall(self.public_key.public_bytes(
                encoding=serial.Encoding.PEM,
                format=serial.PublicFormat.SubjectPublicKeyInfo
            ))
            # Receive server public key
            data = s.recv(8192)
            key = serial.load_pem_public_key(data, default_backend())
            if not isinstance(key, rsa.RSAPublicKey):
                print('Invalid key received. Terminating...')
                s.close()
                self.try_connection()
            if self.server_key is None:
                print('Server public key received.')
                self.server_key = key
                self.continue_connection(s)

    def continue_connection(self, sock):
        pass

    def encrypt_data(self, data: str) -> bytes:
        return self.server_key.encrypt(data.encode('utf-8'), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                          algorithm=hashes.SHA256(),
                                                                          label=None))

    def decrypt_data(self, data: bytes) -> str:
        cipher = self.private_key.decrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                             algorithm=hashes.SHA256(),
                                                             label=None))
        return cipher.decode('utf-8')


class ConnectionSplash(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('New Connection')
        # Keep focus on window
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.remove_item = QPushButton('Remove Item')

        main_layout = QHBoxLayout()

        # Saved IP's
        saved_box = QGroupBox('Saved')
        saved_layout = QVBoxLayout()
        saved_box.setLayout(saved_layout)
        self.save_list = QListWidget()
        self.save_list.addItem('New Connection...')
        self.save_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.loaded_connections = self.load_profiles()
        self.save_list.setCurrentRow(0)
        self.save_list.clicked.connect(self.update_list_functions)
        saved_layout.addWidget(self.save_list)
        self.remove_item.setEnabled(False)
        self.remove_item.clicked.connect(self.remove_selected_item)
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
        self.connect.clicked.connect(self.connect_to_target)
        self.connect.setEnabled(False)
        self.save = QPushButton('Save')
        self.save.clicked.connect(self.save_connection)
        self.save.setEnabled(False)
        connection_options.addWidget(self.save)
        connection_options.addStretch()
        connection_options.addWidget(self.connect)
        connect_layout.addStretch()
        connect_layout.addLayout(connection_options)

        main_layout.addWidget(saved_box)
        main_layout.addWidget(connect_box)
        self.setLayout(main_layout)
        self.exec_()

    def load_profiles(self):
        user_dir = appdirs.user_data_dir('PySmartSwitchClient', 'JackHogan')
        if not isdir(user_dir):
            makedirs(user_dir, exist_ok=True)
        if not isfile(join(user_dir, 'profiles.json')):
            with open(join(user_dir, 'profiles.json'), 'w') as f:
                f.write('{}')
        with open(join(user_dir, 'profiles.json'), 'r+') as json_file:
            profiles = json.load(json_file)
            self.remove_item.setEnabled(len(profiles) > 0)
            for profile in profiles:
                self.save_list.addItem(profile)
            return profiles

    def closeEvent(self, event: QCloseEvent):
        self.save_all_connections()
        sys.exit(0)

    def connect_to_target(self):
        self.save_all_connections()
        self.hide()

    # Checks to make sure that all parameters are filled before allowing save/connection
    def check_arguments(self):
        ok = len(self.address.text()) > 0
        self.save.setEnabled(ok)
        self.connect.setEnabled(ok)

    def save_connection(self):
        title = QInputDialog.getText(self, 'Save Connection', 'Input Connection Name:', QLineEdit.Normal, '',
                                     Qt.WindowCloseButtonHint)
        if not title[1]:
            return
        name = title[0]
        if name in self.loaded_connections:
            append_digit = 1
            while (name + ' (' + str(append_digit) + ')') in self.loaded_connections:
                append_digit += 1
            self.loaded_connections[name + ' (' + str(append_digit) + ')'] = (self.address.text(), self.port.value())
            self.save_list.addItem(name + ' (' + str(append_digit) + ')')
        else:
            self.loaded_connections[name] = (self.address.text(), self.port.value())
            self.save_list.addItem(name)
        self.save_list.setCurrentRow(len(self.save_list) - 1)
        self.remove_item.setEnabled(True)

    def update_list_functions(self):
        self.remove_item.setEnabled(not self.save_list.currentItem().text() == 'New Connection...')
        if self.save_list.currentItem().text() == 'New Connection...':
            self.address.setText('')
            self.port.setValue(30000)
        else:
            self.address.setText(self.loaded_connections[self.save_list.currentItem().text()][0])
            self.port.setValue(self.loaded_connections[self.save_list.currentItem().text()][1])

    def remove_selected_item(self):
        self.loaded_connections.pop(self.save_list.currentItem().text())
        self.save_list.takeItem(self.save_list.row(self.save_list.currentItem()))
        self.update_list_functions()

    def save_all_connections(self):
        user_dir = appdirs.user_data_dir('PySmartSwitchClient', 'JackHogan')
        if isfile(join(user_dir, 'profiles.json')):
            remove(join(user_dir, 'profiles.json'))
        with open(join(user_dir, 'profiles.json'), 'w') as f:
            json.dump(self.loaded_connections, f)

    def get_port(self):
        return self.port.value()

    def get_address(self):
        return self.address.text()

    def get_pass(self):
        return self.password.text()
