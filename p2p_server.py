import socket
from config import *
from util import Util

class P2PServer:
    def __init__(self, server_names_client):
        self._server_names_client = server_names_client
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._stop = False
    
    def set_stop(self, truth_value):
        self._stop = truth_value

    def update_p2p_socket(self, ip, new_port):
        self._stop = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.start(ip, new_port)

    def split_message(self, message):
        msg = message.split("::=")
        return msg

    def start(self, server_host, server_port):
        self._stop = False
        server_addr = (server_host, int(server_port)) 
        self._socket.bind(server_addr)
        self._socket.listen()
        print(f'O P2P está ouvindo em {server_addr}')
        
        self._server_names_client.set_listening_server_name(True)
        self.run()

    def run(self):
        self._socket.settimeout(1.0)

        while True:
            try:
                if not self._stop:
                    conn, addr = self._socket.accept()
                    self.handle_client(conn, addr)
                else:
                    break
            except socket.timeout:
                pass
        
        self._socket.close()

    def compute_call_answer(self, valid_answers):
        call_answer = input('> ')
        call_answer = Util.process_input(call_answer, valid_answers)
        if call_answer == 's':
            self._server_names_client.send_server_call_msg(True)

            print('\nInforme a porta para receber os fluxos de áudio:')
            used_ports = self._server_names_client.get_used_ports()
            audio_port = Util.get_port_input(used_ports)
            self._server_names_client.add_used_port(str(audio_port))
            
            print('Informe a porta para receber os fluxos de vídeo:')
            used_ports = self._server_names_client.get_used_ports()
            video_port =  Util.get_port_input(used_ports)
            self._server_names_client.add_used_port(str(video_port))
            answer_msg = f'{SERVER_CALL_ACK}::={audio_port},{video_port}'
            print('Iniciando ligação...')
        else:
            print('Chamada recusada. Esperando nova ligação...')
            self._server_names_client.set_clear_console(False)
            answer_msg = f'{SERVER_CALL_NACK}::='
        
        return answer_msg

    def handle_client(self, conn, addr):
        self._server_names_client.set_listening_server_name(False)
        self._server_names_client.set_in_call(True)
        
        connected = True
        while connected:
            original_msg = conn.recv(SIZE).decode(FORMAT) 
            msg = self.split_message(original_msg) 
            Util.clear_console()
            print(f'[{addr}] {original_msg}')

            if msg[0] == PEER_CALL_REQUEST:
                p2p_client = msg[1].split(',')[0]
                print(f'{p2p_client} está te ligando. Deseja aceitar a ligação?\n \'s\' - sim \n \'n\' - não')
                answer_msg = self.compute_call_answer(['s', 'n'])
                conn.send(answer_msg.encode(FORMAT))

            elif msg[0] == DISCONNECT_MSG:
                connected = False
                self._server_names_client.set_in_call(False)
                self._server_names_client.send_server_call_msg(False)
        
        self._server_names_client.set_listening_server_name(True)
        conn.close()