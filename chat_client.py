from socket import socket
from chat_server import DISCONNECT, AUTH_SUCCESS, encode, decode
from threading import Thread
from argparse import ArgumentParser
from sys import argv


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', default='127.0.0.1')
    parser.add_argument('-p', '--port', default='8001')
    args = parser.parse_args(argv[1:])
    try:
        port = int(args.port)
    except ValueError:
        port = 8001
    return args.address, port


def auth(client: socket) -> bool:
    print(decode(client.recv(1024)))
    while True:
        while True:
            data = input('Your name: ')
            if data and "'" not in data:
                break
            else:
                print('Name must be not empty and must not consist \' symbol')
        client.send(encode(data))
        answer = decode(client.recv(1024))
        if answer == DISCONNECT:
            print('Diconnected!')
            return False
        elif answer == AUTH_SUCCESS:
            print('Authenticated successfully!')
            return True
        else:
            print(answer)

def sender(client: socket):
    global client_alive
    while True:
        msg = input()
        client.sendall(encode(msg))
        if msg == DISCONNECT:
            client_alive = False
            break
    
def main(client: socket):
    if auth(client):
        Thread(target=sender, args=(client,), daemon=True).start()
        while client_alive:
            answer = decode(client.recv(1024))
            print(f'[server]:{answer}')
            if answer == DISCONNECT:
                break

client = socket()
client.connect(parse_args())
client_alive = True

try:
    main(client)
except BrokenPipeError:
    print('Client shutdown by error')
    client.send(encode(DISCONNECT))
except KeyboardInterrupt:
    print('Client shutdown by keyboard interrupt')
    client.send(encode(DISCONNECT))
finally:
    client.close()