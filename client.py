from socket import socket
from server import ADDRESS, PORT, encode, decode, DISCONNECT


client = socket()

client.connect((ADDRESS, PORT))

print('Добро пожаловать на сервер квадратов!')

while True:
    msg = input(f'Введите число ({DISCONNECT} для выхода): ')
    client.send(encode(msg))
    if msg == DISCONNECT:
        client.close()
        break
    print(f'Сервер ответил: {decode(client.recv(100))}')

print('До свидания, до новых встреч на сервере квадратов!')
