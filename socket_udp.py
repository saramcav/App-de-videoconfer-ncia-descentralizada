import socket
from config import *

class SocketUDP:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def split_message(self, message):
        msg = message.split("::=")
        return msg

    def start_server(self, server_p2p_host, server_p2p_port):
        server_p2p_addr = (server_p2p_host, int(server_p2p_port))
        self._socket.bind(server_p2p_addr)
        self.run_server()

    def run_server(self):
        while True:
            data, addr = self._socket.recvfrom(SIZE)
            print(f'[P2P CLIENTE - {addr}] {data}')
            received_msg = data.decode(FORMAT)
            received_msg = self.split_message(received_msg)

            #resposta
            msg = 'resposta do servidor'
            bytesToSend = str.encode(msg)
            self._socket.sendto(bytesToSend, addr)
    
    def start_client(self,  server_p2p_host, server_p2p_port):
        server_p2p_addr = (server_p2p_host, int(server_p2p_port))
        self.run_client(server_p2p_addr)
    
    def run_client(self, server_p2p_addr):
        msg = f'aaa'
        bytesToSend = str.encode(msg) 
        self._socket.sendto(bytesToSend, server_p2p_addr)