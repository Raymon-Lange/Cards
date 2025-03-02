import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.86.42"#"136.62.155.123"
        self.port = 5550
        self.addr = (self.server, self.port)
        self.playerId = self.connect()

    def getId(self):
        return self.playerId

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            print("Failed to connect")
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048*4))
        except socket.error as e:
            print(e)