import socket
from config import *

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
    
    def run(self, client_name):
        self._server_names_client.set_listening_server_name(False)
        call_request = f'{PEER_CALL_REQUEST}::={client_name}'
        self._socket.send(call_request.encode(FORMAT)) 

        connected = True
        while connected:
            msg = self._socket.recv(SIZE).decode(FORMAT) 
            print(f'[SERVIDOR P2P] {msg}')
            msg = self.split_message(msg) 

            if msg[0] == SERVER_CALL_ACK:
                name, peer_audio_port, peer_video_port = msg[1].split(',')
                print(f'{name} aceitou a sua ligação. Portas: {peer_audio_port}, {peer_video_port}')

            elif msg[0] == SERVER_CALL_NACK:
                print(f'{msg[1]} recusou a sua ligação. Iniciando ligação...')
                answer_msg = f'{DISCONNECT_MSG}::='
                connected = False
                self._server_names_client.set_rejected_call(True)
                self._socket.send(answer_msg.encode(FORMAT))

        self._server_names_client.set_listening_server_name(True)
        self._socket.close()

