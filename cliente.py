import socket 
from utils import *

class Client:
    def __init__(self, server_host, server_port, name, ip, reception_port):
        self._name = name
        self._ip = ip
        self._reception_port = reception_port
        addr = (server_host, server_port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(addr)
        print(f'[CONEXAO] cliente conectado ao servidor em {server_host}:{server_port}\n')
        self.run()

    def enconde_message(self, message):
        if message == '1':
            message = f'{USER_QUERY_MSG}::='
            message += str(input(f'Insira o usuário a ser buscado> '))
            
        elif message == '2':
            message = f'{DISCONNECT_MSG}::={self._name}'

        elif message == '3':
            message = f'{TABLE_QUERY_MSG}::={self._name}' 

        return message

    def decode_message(self, message):
        msg = message.split("::=")
        return msg
    
    def run(self):     
        msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port}'
        self._socket.send(msg.encode(FORMAT))

        print('Para realizar uma consulta pelo nome de usuário, insira \'1\'')
        print('Para se desvincular do servidor, insira \'2\'')
        print('Para consultar a tabela de clientes conectados no servidor, insira \'3\'\n')

        conectado = True
        while conectado:
            msg = self._socket.recv(SIZE).decode(FORMAT)
            msg = self.decode_message(msg)
            print(f'[SERVIDOR]: {msg[1]}')

            if msg[0] == DISCONNECT_MSG:
                conectado = False

            else:
                msg = str(input(f'> '))
                msg = self.enconde_message(msg)
                self._socket.send(msg.encode(FORMAT))

        self._socket.close()


        

k = Client(host, port, 'Saaara', '192.168.452.238', '5000')