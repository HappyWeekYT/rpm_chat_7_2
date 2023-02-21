from socket import socket
from time import sleep

ADDRESS = '127.0.0.1'
PORT = 8001
DISCONNECT = 'q'

def decode(data: bytes, coding='utf-8') -> str:
    return data.decode(coding)

def encode(text: str, coding='utf-8') -> bytes:
    return text.encode(coding)

def work(working_socket):
    msg = decode(working_socket.recv(100))
    if msg == DISCONNECT:
        return False
    print(f'Received message: {msg}')
    try:
        num = int(msg)
    except:
        out_msg = 'Не мог бы ты отправить число плз?'
    else:
        out_msg = str(num ** 2)
    working_socket.send(encode(out_msg))
    print(f'Sent out_msg: {out_msg}')
    return True

def main():
    server = socket()
    server.bind((ADDRESS, PORT))
    server.listen()
    client, client_addr = server.accept()
    print(f'Подключился новый клиент по адресу: {client_addr}')
    while True:
        if not work(client):
            client.close()
            server.close()
            break

if __name__ == '__main__':
    main()