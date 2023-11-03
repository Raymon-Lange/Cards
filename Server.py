import socket
from _thread import *
import sys

server = "192.168.1.1"
port = 1369

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as error:
    str(error)

s.listen(2)
print("Waiting for a connection, Server has Started")

def threaded_client(conn):
    conn.send(str.encode("Connected"))
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            reply = ""

            if not data: 
                print("Disconnected")
                break
            else:
                print("Received: ", reply)
                print("Sending :", reply)

            conn.sendall(str.encode(reply))
        except:
            break

    print("Lost Connection")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn,))