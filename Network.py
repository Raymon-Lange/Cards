import socket
import pickle
import logging
import time

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Network")

class Network:
    def __init__(self, max_retries=5, retry_delay=2):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"  # inside
        #self.server = "136.62.155.123" #outside 
        self.port = 5550
        self.addr = (self.server, self.port)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.playerId = self.connect()

    def getId(self):
        return self.playerId

    def connect(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Reset socket
                self.client.connect(self.addr)
                logger.info(f"Connected to server {self.server}:{self.port}")
                return self.client.recv(2048).decode()
            except Exception as e:
                retries += 1
                logger.warning(f"Connection attempt {retries}/{self.max_retries} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        logger.error("Max retries reached. Failed to connect to server.")
        return None

    def send(self, data):
        # Send all data in one go
        self.client.sendall(str.encode(data))
        # Receive full response before unpickling
        response = self.client.recv(4096*2)
        if response:
        # Deserialize the complete data only once
            try:
                response = pickle.loads(response)
                return response
            except (pickle.UnpicklingError, EOFError) as e:
                logger.error(f"Failed to unpickle data: {e}")
                return None

