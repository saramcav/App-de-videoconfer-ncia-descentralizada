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
    
    def run(self):     
        msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port}'
        self._socket.send(msg.encode(FORMAT))

        print('Para realizar uma consulta pelo nome de usuário, insira \'1\'')
        print('Para se desvincular do servidor, insira \'2\'\n')

        while True:
            #Insira seu nome, IP e porta para recepção de chamadas:
            msg = str(input(f'> '))
            
            if msg == '1':
                msg = f'{USER_QUERY_MSG}::='
                msg += str(input(f'Insira o usuário a ser buscado> '))
            
            elif msg == '2':
                msg = f'{DISCONNECT_MSG}::={self._name}'


            self._socket.send(msg.encode(FORMAT))
            # else:
            #     msg = self._socket.recv(SIZE).decode(FORMAT)
            #     print(f'[SERVIDOR] {msg}')
    

k = Client(host, port, 'Sara', '192.168.252.228', '5000')