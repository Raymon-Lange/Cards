import socket
import logging
from _thread import *
import pickle
from Game import *
import sys

# Configure logger
logging.basicConfig(filename='server.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GameServer")

server = '0.0.0.0'
port = 5550

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    logger.error(f"Socket binding error: {e}")
    sys.exit()

s.listen(2)
logger.info("Waiting for a connection, Server Started")

connected = set()
games = {}
idCount = 0

def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    logger.info(f"Player {p} connected to game {gameId}")

    while True:
        try:
            data = conn.recv(4096).decode()

            if gameId in games:
                board = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        board.reset()
                        logger.info(f"Game {gameId} reset by Player {p}")
                    elif data != "get":
                        board.play(data, p)
                        logger.info(f"Game {gameId}: Player {p} played {data}")

                    conn.sendall(pickle.dumps(board))
            else:
                break
        except Exception as error:
            logger.error(f"An error occurred: {error}")
            break

    logger.info("Lost connection")
    try:
        del games[gameId]
        logger.info(f"Closing Game {gameId}")
    except KeyError:
        pass
    #idCount -= 1 Do we really care that lost connection
    conn.close()

while True:
    conn, addr = s.accept()
    logger.info(f"Connected to: {addr}")

    idCount += 1
    p = 0
    gameId = (idCount - 1) // 2
    if idCount % 2 == 1:
        games[gameId] = Board(gameId)
        logger.info(f"Creating a new game {gameId}")
    else:
        #games[gameId].ready = True
        games[gameId].startGame()
        p = 1
        logger.info(f"Game {gameId} is now ready")

    start_new_thread(threaded_client, (conn, p, gameId))