import socket
import threading
import sys
import time

from AES_lib import gen_key
from client import Client, Q_Key_Exchange

server_sock = ['0.0.0.0', 55555]

# if len(sys.argv) > 2:
#     server_sock[1] = sys.argv[1]
# if len(sys.argv) > 2:
#     server_sock[2] = int(sys.argv[2])

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(tuple(server_sock))
server.listen()

stop = False

# Lists For Clients and 
clients = []

# Sending Messages To All Connected Clients
def broadcast(message, sender):
    for client in clients:
        if client != sender:
            client.send(message)

# Handling Messages From encrypt
def handle(client: Client):
    client.set_nickname(client.recv())
    broadcast(f"{client.nick} was joined!", client)
    while not stop:
        try:
            # Broadcasting Messages
            message = client.recv()
            broadcast(f"{client.nick}: {message}", client)
        except:
            # Removing And Closing Client
            clients.pop(clients.index(client))
            client.close()
            broadcast(f'{client.nick} left!', client)
            break


# Receiving / Listening Function
def receive():
    while not stop:
        # Accept Connection
        sock, address = server.accept()
        print(f"Connected with {address}")

        # create client with new key
        key = None
        if '-q' in sys.argv:
            key = Q_Key_Exchange(sock).do_alice_part()
            client = Client(gen_key(key), sock)
        else:
            client = Client(gen_key(key), sock)
            client.key_exchange()
        clients.append(client)

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive_thread = threading.Thread(target=receive)
receive_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("quitting")
    stop = True
    sys.exit()
