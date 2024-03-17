import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.getcwd(), '..'))


from common.security_wrapper import SecurityWrapper


class Server(SecurityWrapper):
    def __init__(self):
        self.clients = {}

        super().__init__('localhost', 9024)
        print(f'Server: {self.host}:{self.port}')

    def _receive(self, data, addr):
        if data == b'echo':
            self.send(b'Hello from server!', addr)


if __name__ == '__main__':
    server = Server()
    server.receive()
