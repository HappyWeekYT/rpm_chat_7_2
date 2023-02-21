from socket import socket
from chat_server import ADDRESS, PORT, DISCONNECT, AUTH_SUCCESS,  encode, decode
from threading import Thread


def auth(client: socket) -> bool:
    print(decode(client.recv(1024)))
    while True:
        while True:
            data = input('Your name: ')
            if data:
                break
            else:
                print('Name must be not empty')
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

def receive(client):
    while True:
        print(f'[server]:{decode(client.recv(1024))}') #NOTE

client = socket()
client.connect((ADDRESS, PORT))

if auth(client):
    Thread(target=receive, args=(client,), daemon=True).start()
    while True:
        msg = input() # убрать текст
        client.send(encode(msg))
        if msg == DISCONNECT:
            break
client.close()