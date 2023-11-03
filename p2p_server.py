import socket
import os
from utils import *

class P2PServer:
    def __init__(self, server_names_client):
        self._server_names_client = server_names_client
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def split_message(self, message):
        msg = message.split("::=")
        return msg

    def start(self, server_host, server_port):
        server_addr = (server_host, int(server_port)) 
        self._socket.bind(server_addr)
        self._socket.listen()
        print(f'O P2P está ouvindo em {server_addr}')
        self.run()

    def run(self):
        conectado = True
        while conectado:
            conn, addr = self._socket.accept()
            msg = conn.recv(SIZE).decode(FORMAT) 
            msg = self.split_message(msg) 

            if msg[0] == PEER_CALL_REQUEST:
                self._server_names_client.set_listening_server_name(False)
                #self.clear_console()
                print(f'{msg[1]} está te ligando. Deseja aceitar a ligação?\n \'s\' - sim \n \'n\' - não')
                call_answer = input('AAAA> ')
                if call_answer == 's':
                    print('Informe a porta para receber os fluxos de áudio:')
                    audio_port = int(input('> '))
                    print('Informe a porta para receber os fluxos de vídeo:')
                    video_port = int(input('> '))
                    answer_msg = f'{SERVER_CALL_ACK}::={msg[1]},{audio_port},{video_port}'
                else:
                    print('Chamada recusada. Esperando nova ligação...')
                    self._server_names_client.set_listening_server_name(True)
                    answer_msg = f'{SERVER_CALL_NACK}::={msg[1]}'
                conn.send(answer_msg.encode(FORMAT))
        
            elif msg[0] == DISCONNECT_MSG:
                print('alowjdwjd')
                conectado = False

        conn.close()