import os
from common.security_wrapper import SecurityWrapper


class Server(SecurityWrapper):
    def __init__(self):
        self.clients = {}

        super().__init__(os.environ.get('SERVER_HOST', 'localhost'), int(os.environ.get('SERVER_PORT', '9024')))
        print(f'Server: {self.host}:{self.port}')

    def _receive(self, data, addr):
        if data == b'echo':
            self.send(b'Hello from server!', addr)


if __name__ == '__main__':
    server = Server()
    server.receive()
