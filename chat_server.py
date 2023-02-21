from socket import socket
from dotenv import load_dotenv
from os import getenv
from threading import Thread, Lock


load_dotenv()

ADDRESS = getenv('ADDRESS')
DISCONNECT = getenv('DISCONNECT')
AUTH_SUCCESS = getenv('AUTH_SUCCESS')
try:
    PORT = int(getenv('PORT'))
except ValueError:
    PORT = 8001

def encode(text: str, coding='utf-8') -> bytes:
    return text.encode(coding)

def decode(data: bytes, coding='utf-8') -> str:
    return data.decode(coding)

def auth(client: socket, cl_address: tuple) -> str: # меняем
    global clients, clients_lock # меняем
    client.send(encode(getenv('GREETING', default='Henlo')))
    while True:
        data = decode(client.recv(20))
        if data == DISCONNECT:
            msg = DISCONNECT
            client.send(encode(msg))
            # меняем
            print(f'Client {cl_address} doesn\'t want to speak with us :\'(')
            return # меняем
        if data:
            # TODO нужно проверять, есть ли такой ник!
            msg = AUTH_SUCCESS
            client.send(encode(msg))
            with clients_lock:
                clients[data] = client # меняем
            print(f'Client {cl_address} is authenticated by name {data}') # меняем   
        else:
            msg = 'Please input non-empty name!'
            client.send(encode(msg))

def accept(server):
    while True:
        client, cl_address = server.accept()
        print(f'Client {cl_address} connected!')
        Thread(target=auth, args=(client, cl_address), daemon=True).start()

def main(server: socket) -> None:
    server.bind((ADDRESS, PORT))
    server.listen()
    Thread(target=accept, args=(server,), daemon=True).start()
    while True:
        if clients:
            msg, _ = decode(server.recv(1024))  # меняем
            if msg == DISCONNECT:
                server.close()
                break
            print(f'Message: {msg}') # меняем

if __name__ == '__main__':
    server = socket()
    clients: dict = {}
    clients_lock = Lock()

    if not (DISCONNECT and AUTH_SUCCESS):
        print('Error: serving messages have not been loaded')
    else:
        try:
            main(server)
        except BrokenPipeError:
            server.close()
        except KeyboardInterrupt:
            server.close()