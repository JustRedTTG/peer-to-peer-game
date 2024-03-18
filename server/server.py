import os
import sys
from logging import info

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.getcwd(), '..'))


from common.security_wrapper import SecurityWrapper


class Server(SecurityWrapper):
    def __init__(self):
        self.clients = {}

        super().__init__('0.0.0.0', 9024)
        info(f'Server running on: {self.host}:{self.port}')

    def _receive(self, data, addr):
        if data == b'echo':
            info(f'Received an echo request from {addr}')
            self.send(b'Hello from server!', addr)


if __name__ == '__main__':
    server = Server()
    server.receive()
