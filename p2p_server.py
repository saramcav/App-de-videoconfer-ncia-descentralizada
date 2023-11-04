import socket
import threading
from config import *
from util import Util

class P2PServer:
    def __init__(self, server_names_client):
        self._server_names_client = server_names_client
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        while True:
            conn, addr = self._socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
        
    def handle_client(self, conn, addr):
        connected = True
        while connected:
            msg = conn.recv(SIZE).decode(FORMAT) 
            msg = self.split_message(msg) 

            if msg[0] == PEER_CALL_REQUEST:
                self._server_names_client.set_listening_server_name(False)
                #Util.clear_console()
                
                print(f'{msg[1]} está te ligando. Deseja aceitar a ligação?\n \'s\' - sim \n \'n\' - não')
                call_answer = input('AAAA> ')
                if call_answer == 's':
                    print('Informe a porta para receber os fluxos de áudio:')
                    audio_port = Util.get_port_input()
                    print('Informe a porta para receber os fluxos de vídeo:')
                    video_port =  Util.get_port_input()
                    answer_msg = f'{SERVER_CALL_ACK}::={msg[1]},{audio_port},{video_port}'
                else:
                    print('Chamada recusada. Esperando nova ligação...')
                    #self._server_names_client.set_listening_server_name(True)
                    answer_msg = f'{SERVER_CALL_NACK}::={msg[1]}'
                conn.send(answer_msg.encode(FORMAT))
        
            elif msg[0] == DISCONNECT_MSG:
                connected = False
                self._server_names_client.set_listening_server_name(True)

        conn.close()