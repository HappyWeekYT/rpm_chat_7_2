from socket import socket
from dotenv import load_dotenv
from os import getenv
from threading import Thread, Lock


load_dotenv()

ADDRESS: str = getenv('ADDRESS')
DISCONNECT: str = getenv('DISCONNECT')
AUTH_SUCCESS: str = getenv('AUTH_SUCCESS')
SHUTDOWN: str = getenv('SHUTDOWN', default='/shutdown')
LIST: str = getenv('LIST', default='/list')
HELP: str = getenv('HELP', default='/help')
WHISPER: str = getenv('WHISPER', default='/whisper')
CL_LIST: str = getenv('CL_LIST', default='/list')
try:
    PORT = int(getenv('PORT'))
except ValueError:
    PORT = 8001

def encode(text: str, coding='utf-8') -> bytes:
    return text.encode(coding)

def decode(data: bytes, coding='utf-8') -> str:
    return data.decode(coding)

def enum_clients() -> str:
    global clients, clients_lock
    with clients_lock:
        return '\n' + '\n'.join([f'{num}. {name}' for num, name in enumerate(clients.keys())])

def send_all(msg: str, except_name: str = None):
    global clients_lock, clients
    with clients_lock:
        clients_names = list(clients.keys()) 
        if except_name:
            clients_names.remove(except_name)
        for name in clients_names:
            clients[name].send(encode(msg))

def receiver(client: socket, cl_name: str):
    global clients, clients_lock
    while True:
        msg = decode(client.recv(1024))
        if msg == DISCONNECT:
            client.close()
            with clients_lock:
                del clients[cl_name]
                disconnect_msg = f'Client {cl_name} has disconnected from server'
                print(disconnect_msg)
                for cl_socket in clients.values():
                    cl_socket.send(encode(disconnect_msg))
            break
        # если не disconnect, то проверяем на команду списка клиентов
        elif msg == CL_LIST:
            client.send(encode(enum_clients()))
        elif msg.startswith(WHISPER):
            msg_parts = msg.split()
            if len(msg_parts) >= 3:
                target_name = msg_parts[1]
                target_msg = ' '.join(msg_parts[2:])
                with clients_lock:
                    target_socket = clients.get(target_name) # убрать default
                    if target_socket:
                        server_msg = f'{cl_name} whispered: {target_msg}'
                        target_socket.send(encode(server_msg))
                    else:
                        client.send(encode('There is no client with such name'))
            else:
                client.send(encode('Incorrect command format, usage:\n/whisper name message '))
        # или выводим сообщение от клиента на сервере
        else:
            server_msg = f'{cl_name}: {msg}'
            print(server_msg)
            # рассылка сообщения от пользователя всем остальным, кроме него самого
            send_all(server_msg, cl_name)

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
            if data in clients.keys(): # если среди ников такой уже есть
                msg = 'The name is already taken, choose another name'
                client.send(encode(msg))
            else:
                msg = AUTH_SUCCESS
                client.send(encode(msg))
                with clients_lock:
                    clients[data] = client # меняем
                print(f'Client {cl_address} is authenticated by name {data}') # меняем
                # запускаем поток приёма сообщений от клиента
                Thread(target=receiver, args=(client, data), daemon=True).start()
                break
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
        user_inp = input()
        if user_inp == SHUTDOWN:
                for cl_socket in clients.values():
                    cl_socket.send(encode(DISCONNECT))
                    cl_socket.close()
                break
        elif user_inp == LIST:
            print(enum_clients())
        elif user_inp == HELP:
            print('List of commands:\n/shutdown \n/help\n/list')


if __name__ == '__main__':
    server = socket()
    clients: dict = {} # name: socket
    clients_lock = Lock()

    if not (DISCONNECT and AUTH_SUCCESS):
        print('Error: serving messages have not been loaded')
    else:
        try:
            main(server)
        except BrokenPipeError:
            print('Server shutdown by error')
        except KeyboardInterrupt:
            print('Server shutdown by keyboard interrupt')
        finally:
            server.close()