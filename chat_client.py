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
client.connect((ADDRESS, PORT))
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