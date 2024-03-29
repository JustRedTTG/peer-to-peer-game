import os
import sys
import random
import threading
import uuid
from typing import Tuple
from dotenv import load_dotenv

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.getcwd(), '..'))

from common.security_wrapper import SecurityWrapper

try:
    load_dotenv('../.env-client')
except FileNotFoundError:
    pass

SERVER_HOST = os.environ.get('SERVER_HOST', '127.0.0.1')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '9024'))

print(f'Server is: {SERVER_HOST}:{SERVER_PORT}')


class Client(SecurityWrapper):
    address: Tuple[str, int] = None
    TIMEOUT_TIME = 5
    HEARTBEAT_TIME = 1.5
    SERVER = (SERVER_HOST, SERVER_PORT)

    @staticmethod
    def get_port():
        return random.randint(10000, 40000)

    def __init__(self, host: str = 'localhost', port: int = None, echo_mode=False):
        self.identifier = uuid.uuid4()
        self.echo_mode = echo_mode
        super().__init__(host, port or self.get_port())
        print(f'Client: {self.host}:{self.port}')

    def echo(self):
        if not self.echo_mode:
            raise Exception("Echo mode is disabled")
        self.send(b'echo', self.SERVER)

    def _receive(self, data: bytes, addr: Tuple[str, int]):
        if self.echo_mode and data == b'Hello from server!':
            self.send(b'Hello from client!', addr)
            print("Received echo from server")
            self.receiving = False

    def thread_receive(self):
        threading.Thread(target=self.receive, daemon=False).start()


if __name__ == '__main__':
    client = Client(echo_mode=True)
    client.thread_receive()
    print("Please note that this script isn't meant to be executed directly. Running a server echo now...")
    client.echo()
