import socket

PORT = 30011


class Client:
    def __init__(self):
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
