import socket
from configs.config import *
from configs.util import Util
from vidstream import *
import threading

class P2PServer:
    def __init__(self, server_names_client):
        self._server_names_client = server_names_client
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._stop = False
        self._ip = None
    
    def set_stop(self, truth_value):
        self._stop = truth_value

    def update_p2p_socket(self, ip, new_port):
        # Atualiza o socket P2P com um novo endereço IP e porta.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start(ip, new_port)

    def start(self, server_host, server_port):
        # Inicia o servidor P2P, vinculando-o a um endereço IP e porta específicos.
        self._stop = False
        server_addr = (server_host, int(server_port)) 
        self._ip = server_host
        self._socket.bind(server_addr)
        self._socket.listen()
        print(f'O P2P está ouvindo em {server_addr}')
        
        self._server_names_client.set_listening_server_name(True)
        self.run()

    def run(self):
        # Executa o loop principal do servidor P2P, aguardando conexões de clientes.
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
        # Solicita e processa a resposta do usuário para uma chamada de P2P.
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
        
        return [audio_port, video_port, answer_msg]

    def handle_client(self, conn, addr):
        # Lida com a comunicação com um cliente P2P, aceitando ou recusando chamadas.
        self._server_names_client.set_listening_server_name(False)
        self._server_names_client.set_in_call(True)
        
        connected = True
        while connected:
            original_msg = conn.recv(SIZE).decode(FORMAT) 
            msg = Util.split_message(original_msg) 
            Util.clear_console()
            print(f'[{addr}] {original_msg}')

            if msg[0] == PEER_CALL_REQUEST:
                p2p_client = msg[1].split(',')[0]
                p2p_client_ip = msg[1].split(',')[3]
                p2p_client_video_port = msg[1].split(',')[2]
                p2p_client_audio_port = msg[1].split(',')[1]
                print(f'{p2p_client} está te ligando. Deseja aceitar a ligação?\n \'s\' - sim \n \'n\' - não')
                answer_msg = self.compute_call_answer(['s', 'n'])
                conn.send(answer_msg[-1].encode(FORMAT))
                video_port = answer_msg[1]
                audio_port = answer_msg[0]
                self._video_receiver = StreamingServer(self._ip, int(video_port))
                self._audio_receiver = AudioReceiver(self._ip, int(audio_port))
                self.start_listening()
                self.start_camera_stream(p2p_client_ip, p2p_client_video_port)
                self.start_audio_stream(p2p_client_ip, p2p_client_audio_port)

            elif msg[0] == DISCONNECT_MSG:
                connected = False
                self._server_names_client.set_in_call(False)
                self._server_names_client.send_server_call_msg(False)
            
        self._server_names_client.set_listening_server_name(True)
        conn.close()

    def start_listening(self): 
        # Inicializa threads responsáveis pelos canais que vão receber áudio e vídeo de outro usuário.
        self._t1 = threading.Thread(target=self._video_receiver.start_server)
        self._t2 = threading.Thread(target=self._audio_receiver.start_server)
        self._t1.start()
        self._t2.start()

    def start_camera_stream(self, ip, video_port): 
        # Inicializa a thread responsável por enviar o vídeo para outro usuário.
        self._camera_client = ScreenShareClient(ip, int(video_port))
        self._t3 = threading.Thread(target=self._camera_client.start_stream)
        self._t3.start()

    def start_audio_stream(self, ip, audio_port): 
        # Inicializa a thread responsável por enviar o áudio para outro usuário.
        self._audio_sender = AudioSender(ip, int(audio_port))
        self._t4 = threading.Thread(target=self._audio_sender.start_stream)
        self._t4.start()
