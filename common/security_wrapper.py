import base64
import threading
import time
from logging import debug
from socket import socket, AF_INET, SOCK_DGRAM
from hexicapi.encryption import *


class SecurityWrapper:
    def __init__(self, host: str, port: int):
        self.host = '0.0.0.0' if host is None else '0.0.0.0' if host == 'localhost' else host
        self.port = port

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        self.private_key, self.public_key = generate_keys()

        self.addressbook = {}
        self.connected_clients = []
        self.receiving = False

    def encrypt(self, data: bytes, addr) -> bytes:
        return base64.b64encode(self.addressbook[addr].encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ))

    def decrypt(self, data: bytes) -> bytes:
        return self.private_key.decrypt(
            base64.b64decode(data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def _receive(self, addr, data):
        print(f"Received tag from {addr}: {data.decode()}")

    def receive(self):
        self.receiving = True
        while self.receiving:
            try:
                data, addr = self.socket.recvfrom(1024)
            except:
                if not self.receiving:
                    return
                continue
            if addr not in self.addressbook or b'BEGIN PUBLIC KEY' in data:
                self.addressbook[addr] = serialization.load_pem_public_key(data)
                if addr not in self.connected_clients:
                    self.socket.sendto(self.public_key, addr)
                    self.connected_clients.append(addr)
            else:
                decrypted_data = self.decrypt(data)
                self._receive(decrypted_data, addr)

    def send(self, data: bytes, addr: tuple, delay: float = 0.0):
        if delay > 0:
            time.sleep(delay)
        if addr in self.addressbook:
            self.socket.sendto(self.encrypt(data, addr), addr)
        else:
            self.socket.sendto(self.public_key, addr)
            self.connected_clients.append(addr)
            thread = threading.Thread(target=self.send, args=(data, addr, .5), daemon=True)
            thread.start()
            thread.join()
