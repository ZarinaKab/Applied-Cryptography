import sys
import time
import socket
import threading
from sys import argv

from client import Client, Q_Key_Exchange
from AES_lib import gen_key

stop = False

# Listening to Server and Sending Nickname
def receive(server: Client, nickname: str):
    while not stop:
        try:
            # Receive Message From Server
            message = server.recv()
            print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            server.close()
            break

# Sending Messages To Server
def write(server: Client):
    while not stop:
        try: 
            message = input()
            server.send(message)
        except: 
            break

# Choosing Nickname
nickname = input("Choose your nickname: ")

server_sock = ['127.0.0.1', 55555]

# if len(sys.argv) > 2:
#     server_sock[1] = sys.argv[1]
# if len(sys.argv) > 2:
#     server_sock[2] = int(sys.argv[2])

# Connecting To Server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(tuple(server_sock))


key = None
if '-q' in sys.argv:
    key = gen_key(Q_Key_Exchange(sock).do_bob_part())
else:
    key = Client.get_key(sock)

server = Client(key, sock)
server.send(nickname)

receive_thread = threading.Thread(target=receive, args=(server, nickname))
receive_thread.start()

write_thread = threading.Thread(target=write, args=(server, ))
write_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("quitting")
    stop = True
    sys.exit()

