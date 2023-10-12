import socket
import threading
from utils import *

class ClientRegister:
    def __init__(self, ip, reception_port):
        self._ip = ip
        self._reception_port = reception_port
    
    def get_ip(self):
        return self._ip

    def get_reception_port(self):
        return self._reception_port

class Server:
    def __init__(self, host, port):
        self._clients = {}
        self._clients['A'] = ClientRegister('22', '33')
        addr = (host, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(addr)
        self._socket.listen()
        print(f'O servidor está ouvindo em {host}:{port}')
        self.run()
    
    def run(self):
        while True:
            conn, addr = self._socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f'[CONEXOES ATIVAS] {threading.active_count() - 1}')
    
    def handle_client(self, conn, addr):
        conectado = True
        while conectado:
            msg = conn.recv(SIZE).decode(FORMAT)
            print(f'[{addr}] {msg}')
            msg = self.decode_message(msg)

            if msg[0] == DISCONNECT_MSG:
                client = msg[1]
                print(f'[CLIENTE DESCONECTADO] {client} deixou o servidor ...')
                print(f'[CONEXOES ATIVAS] {threading.active_count() - 1}')
                msg = f'{DISCONNECT_MSG}::=VOCÊ FOI DESCONECTADO!'
                conectado = False

            elif msg[0] == NEW_REGISTER_MSG:
                name, ip, reception_port = msg[1].split(',')
                msg = self.add_client_register(name, ip, reception_port)
                print(self.clients_table())
            
            elif msg[0] == USER_QUERY_MSG:
                name = msg[1]
                msg = f'{USER_QUERY_MSG}::={self.query_user(name)}'

            elif msg[0] == TABLE_QUERY_MSG:
                name = msg[1]
                msg = f'{TABLE_QUERY_MSG}::={self.clients_table()}'

            else:
                msg = "[WARNING]::=TENTE NOVAMENTE"
            
            conn.send(msg.encode(FORMAT))
            
        conn.close()
    
    
    def decode_message(self, message):
        msg = message.split("::=")
        return msg
        
            
    def add_client_register(self, name, ip, reception_port):
        if self._clients.get(name) is None: 
            self._clients[name] = ClientRegister(ip, reception_port)
            msg = f'[SUCESSO NO REGISTRO]::={name} inserido/a!'
        else:
            msg = '[FALHA DE REGISTRO]::=Você já está cadastrado!'  
        return msg


    def query_user(self, client_name):
        client = self._clients.get(client_name)

        if client is None:
            msg = '[FALHA NA CONSULTA] O usuário informado não existe!'
        else:
            msg = f'NOME: {client_name:<12} | IP: {client.get_ip():<20} | RECEPTION_PORT: {client.get_reception_port():<6}'
        return msg
    
    def clients_table(self):
        msg = f'{"NOME":<12} | {"IP":<20} | {"PORTA":<6}\n'
        msg += '-' * 60 + '\n'
        for name in self._clients:
            client = self._clients.get(name)
            msg += f'{name:<12} | {client.get_ip():<20} | {client.get_reception_port():<6}\n'
            msg += '-' * 60 + '\n'
        return msg

s = Server(host, port)