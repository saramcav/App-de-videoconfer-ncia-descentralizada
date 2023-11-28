import socket
from configs.config import *
from configs.util import Util
from vidstream import *
import threading

class P2PClient:
    def __init__(self, server_names_client):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_names_client = server_names_client
        self._video_receiver = None
        self._audio_receiver = None
    
    def start(self, server_name, server_host, server_port, client_ip, client_name, audio_port, video_port):    
        # Inicia o cliente P2P, conectando-se ao servidor P2P com os parâmetros fornecidos.
        server_addr = (server_host, int(server_port)) 
        self._ip = client_ip
        self._server_ip = server_host
        self._socket.connect(server_addr)
        self._video_receiver = StreamingServer(client_ip, int(video_port))
        self._audio_receiver = AudioReceiver(client_ip, int(audio_port))
        self.run(server_name, client_name, audio_port, video_port)
    
    def run(self, server_name, client_name, audio_port, video_port):
        # Executa o loop principal do cliente P2P, enviando uma solicitação de chamada e aguardando resposta.
        call_request = f'{PEER_CALL_REQUEST}::={client_name},{audio_port},{video_port},{self._ip}'
        self._socket.send(call_request.encode(FORMAT)) 

        connected = True
        while connected:
            original_msg = self._socket.recv(SIZE).decode(FORMAT) 
            msg = Util.split_message(original_msg) 
            Util.clear_console()
            print(f'[SERVIDOR P2P] {original_msg}')

            if msg[0] == SERVER_CALL_ACK: 
                # Se o outro usuário aceitou a ligação, recebemos um ACK e inicializamos a chamada.
                peer_audio_port, peer_video_port = msg[1].split(',')
                print(f'{server_name} aceitou a sua ligação. Portas: {peer_audio_port}, {peer_video_port}')
                print('Iniciando ligação...')
                self.start_listening()
                self.start_camera_stream(int(peer_video_port))
                self.start_audio_stream(int(peer_audio_port))
                
            elif msg[0] == SERVER_CALL_NACK: 
                # Se o outro usuário recusou a ligação, recebemos um NACK.
                print(f'{server_name} recusou a sua ligação. Desconectando-se...')
                answer_msg = f'{DISCONNECT_MSG}::=Encerrando conexão...'
                self._server_names_client.set_clear_console(False)
                self._server_names_client.send_server_call_msg(False)
                connected = False
                self._socket.send(answer_msg.encode(FORMAT))

        self._server_names_client.set_listening_server_name(True)
        self._socket.close()
    
    def start_listening(self): 
        # Inicializa threads responsáveis pelos canais que vão receber áudio e vídeo de outro usuário.
        self._t1 = threading.Thread(target=self._video_receiver.start_server)
        self._t2 = threading.Thread(target=self._audio_receiver.start_server)
        self._t1.start()
        self._t2.start()

    def start_camera_stream(self, video_port): 
        # Inicializa a thread responsável por enviar o vídeo para outro usuário.
        self._camera_client = CameraClient(self._server_ip, int(video_port))
        self._t3 = threading.Thread(target=self._camera_client.start_stream)
        self._t3.start()

    def start_audio_stream(self, audio_port): 
        # Inicializa a thread responsável por enviar o áudio para outro usuário.
        self._audio_sender = AudioSender(self._server_ip, audio_port)
        self._t4 = threading.Thread(target=self._audio_sender.start_stream)
        self._t4.start()