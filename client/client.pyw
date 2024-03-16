import random
import time
import uuid
from typing import Any, Tuple

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


class Client(DatagramProtocol):
    address: Tuple[str, int] = None
    TIMEOUT_TIME = 5
    HEARTBEAT_TIME = 1.5

    @staticmethod
    def get_port():
        return random.randint(10000, 40000)

    def __init__(self, host: str = None, port: int = None):
        self.identifier = uuid.uuid4()
        self.host = '127.0.0.1' if host is None or host == 'localhost' else host
        self.port = port or self.get_port()
        self.connected = False
        self.heartbeat_last_seen = 0
        print(f'Client: {self.host}:{self.port}')

    def connect(self, host, port):
        self.address = (host, port)
        self.connected = True
        self.heartbeat_last_seen = time.time()
        reactor.callInThread(self.heartbeat)

    def startProtocol(self):
        self.connect(input('Host: ') or '127.0.0.1', int(input('Port: ')))


    def datagramReceived(self, datagram: bytes, addr: Any) -> None:
        if datagram == b'heartbeat':
            self.heartbeat_last_seen = time.time()
        print(addr, datagram.decode())

    def heartbeat(self):
        while self.connected:
            self.transport.write(b'heartbeat', self.address)
            time.sleep(self.HEARTBEAT_TIME)
            self.connected = time.time() - self.heartbeat_last_seen < self.TIMEOUT_TIME
        print('Disconnected')

    def listen(self):
        reactor.listenUDP(self.port, self)


if __name__ == '__main__':
    client = Client()
    client.listen()
    reactor.run()
