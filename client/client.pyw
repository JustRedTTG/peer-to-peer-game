import os
import random
import threading
import time
import uuid
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Any, Tuple
from security_wrapper import SecurityWrapper

SERVER_HOST = os.environ.get('SERVER_HOST', '127.0.0.1')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 9024))


class Client(SecurityWrapper):
    address: Tuple[str, int] = None
    TIMEOUT_TIME = 5
    HEARTBEAT_TIME = 1.5

    @staticmethod
    def get_port():
        return random.randint(10000, 40000)

    def __init__(self, host: str = None, port: int = None):
        self.identifier = uuid.uuid4()
        super().__init__(host or 'localhost', port or self.get_port())
        print(f'Client: {self.host}:{self.port}')

    def start(self):
        self.socket.connect((SERVER_HOST, SERVER_PORT))
        self.send(b'ready', (SERVER_HOST, SERVER_PORT))

    def _receive(self, data: bytes, addr: Tuple[str, int]):
        print(f"Received tag from {addr}: {data.decode()}")
        self.send(b'Hello from client!', addr)


if __name__ == '__main__':
    client = Client()
    threading.Thread(target=client.receive, daemon=False).start()
    client.start()
