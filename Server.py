import socket
from _thread import *
import pickle
from Game import *
import sys

server = "localhost"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

connected = set()
games = {}
idCount = 0


def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    print("Player", p, "from game id", gameId)

    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()

            print("Player", p, "from game id", gameId,"sent",data)

            if gameId in games:
                board = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        board.reset()
                    elif data != "get":
                        board.play(data,p)

                    conn.sendall(pickle.dumps(board))
            else:
                break
        except Exception as error:
            print("An error occured", error)
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1)//2
    if idCount % 2 == 1:
        games[gameId] = Board(gameId)
        print("Creating a new game...")
    else:
        games[gameId].ready = True
        p = 1


    start_new_thread(threaded_client, (conn, p, gameId))