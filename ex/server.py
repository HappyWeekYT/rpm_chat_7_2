from socket import socket
from time import sleep


ADDRESS = '127.0.0.1'
PORT = 8081

def encode(text: str, coding='utf-8'):
    return text.encode(coding)

def decode(text: str, coding='utf-8'):
    return text.decode(coding)

def main():
    server = socket()
    server.bind((ADDRESS, PORT))
    server.listen()

    client, client_addr = server.accept()
    print('Client connected from:', client_addr)
    while True:

        data = input('Что отправить клиенту? (q для выхода)')
        if data == 'q':
            print('До свидания!')
            client.send(encode('Отключен сервером'))
            client.close()
            server.close()
            break
        client.send(encode(data))
        sleep(2)

if __name__ == '__main__':
    main()
