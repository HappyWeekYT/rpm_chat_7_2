from socket import socket
from dotenv import load_dotenv
from os import getenv
from threading import Thread, Lock
from psycopg2 import connect
from time import sleep

load_dotenv()

################################################
PG_HOST: str = getenv('PG_HOST')
PG_DBNAME: str = getenv('PG_DBNAME')
PG_USER: str = getenv('PG_USER')
PG_PASSWORD: str = getenv('PG_PASSWORD')
try:
    PG_PORT: str = getenv('PG_PORT')
except ValueError:
    PG_PORT = 5433
################################################
ADDRESS: str = getenv('ADDRESS')
DISCONNECT: str = getenv('DISCONNECT')
AUTH_SUCCESS: str = getenv('AUTH_SUCCESS')
SHUTDOWN: str = getenv('SHUTDOWN', default='/shutdown')
LIST: str = getenv('LIST', default='/list')
HELP: str = getenv('HELP', default='/help')
WHISPER: str = getenv('WHISPER', default='/whisper')
CL_LIST: str = getenv('CL_LIST', default='/list')
BAN: str = getenv('BAN', default='/ban')
SELECTOR_NAME: str = getenv('BAN_NAME_SELECTOR')
#################
INSERT_NAME: str = getenv('BAN_NAME_INSERT')
#########
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
        if except_name and except_name in clients_names:
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


def db_is_banned_name(name: str) -> bool:
    global db_cursor
    db_cursor.execute(SELECTOR_NAME.format(name))
    return bool(db_cursor.fetchall())


def auth(client: socket, cl_address: tuple) -> str: # меняем
    global clients, clients_lock
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
            elif db_is_banned_name(data):
                msg = 'You have been banned from server.'
                client.send(encode(msg))
                sleep(.1)
                client.send(encode(DISCONNECT))
                client.close()
                return
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

def db_ban_name(name: str) -> None:
    global db_cursor, db_connection
    db_cursor.execute(INSERT_NAME.format(name))
    db_connection.commit()

def ban(cmd: str):
    global clients, clients_lock
    cmd_parts = cmd.split()
    if len(cmd_parts) >= 2:
        target_name = ' '.join(cmd_parts[1:])
        with clients_lock:
            if target_name in clients.keys():
                target_socket = clients[target_name]
                target_socket.send(encode('You are permanently banned'))
                target_socket.send(encode(DISCONNECT))
                target_socket.close()
                del clients[target_name]
        db_ban_name(target_name)
        print(f'User {target_name} was banned')

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
        elif user_inp.startswith(BAN): # новое условие
            ban(user_inp)


if __name__ == '__main__':
    server = socket()
    clients: dict = {} # name: socket
    clients_lock = Lock()
    db_connection = connect(dbname=PG_DBNAME, host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASSWORD)
    db_cursor = db_connection.cursor()

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
            db_cursor.close()
            db_connection.close()