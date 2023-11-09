import socket
from config import *
from util import Util

class P2PClient:
    def __init__(self, server_names_client):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_names_client = server_names_client

    def split_message(self, message):
        msg = message.split("::=")
        return msg
    
    def start(self, server_host, server_port, client_name):
        server_addr = (server_host, int(server_port)) 
        self._socket.connect(server_addr)
        self.run(client_name)

    def get_call_ports(self, name, peer_audio_port, peer_video_port):
        print(f'{name} aceitou a sua ligação. Portas: {peer_audio_port}, {peer_video_port}')
        print('\nInforme a porta para receber os fluxos de áudio:')
        used_ports = self._server_names_client.get_used_ports()
        audio_port = Util.get_port_input(used_ports)
        self._server_names_client.add_used_port(str(audio_port))

        print('Informe a porta para receber os fluxos de vídeo:')
        video_port =  Util.get_port_input(used_ports)
        self._server_names_client.add_used_port(str(video_port))

        return f'{CLIENT_CALL_PORT}::={audio_port},{video_port}'
    
    def run(self, client_name):
        self._server_names_client.set_listening_server_name(False)
        call_request = f'{PEER_CALL_REQUEST}::={client_name}'
        self._socket.send(call_request.encode(FORMAT)) 

        connected = True
        while connected:
            original_msg = self._socket.recv(SIZE).decode(FORMAT) 
            msg = self.split_message(original_msg) 
            Util.clear_console()
            print(f'[SERVIDOR P2P] {original_msg}')

            if msg[0] == SERVER_CALL_ACK:
                name, peer_audio_port, peer_video_port = msg[1].split(',')
                answer_msg = self.get_call_ports(name, peer_audio_port, peer_video_port)
                print('Iniciando ligação...')

            elif msg[0] == SERVER_CALL_NACK:
                print(f'{msg[1]} recusou a sua ligação. Desconectando-se...')
                answer_msg = f'{DISCONNECT_MSG}::=Encerrando conexão...'
                self._server_names_client.set_clear_console(False)
                connected = False
            
            self._socket.send(answer_msg.encode(FORMAT))

        self._server_names_client.set_listening_server_name(True)
        self._socket.close()

