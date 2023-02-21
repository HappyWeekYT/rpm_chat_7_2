from socket import socket
from server import ADDRESS, PORT, encode, decode

client = socket()
client.connect((ADDRESS, PORT))

while True:
    data = decode(client.recv(1024))
    print(f'Data from server: {data}')