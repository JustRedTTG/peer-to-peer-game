import os
import ssl
from OpenSSL import SSL
from socket import socket, AF_INET, SOCK_DGRAM
from security_wrapper import SecurityWrapper


class Server(SecurityWrapper):
    def __init__(self):
        self.clients = {}

        super().__init__(os.environ.get('SERVER_HOST', ''), int(os.environ.get('SERVER_PORT', '9024')))

    def _receive(self, data, addr):
        if data == b'echo':
            self.send(b'Hello from server!', addr)


if __name__ == '__main__':
    server = Server()
    server.receive()
