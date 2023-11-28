import socket
import getpass
import threading
from configs.config import *
from p2p.p2p_client import P2PClient
from p2p.p2p_server import P2PServer
from configs.util import Util
import time
import os
if os.name == 'nt':
    import msvcrt
else:
    import sys
    import termios
    import tty
    import select

class Client:
    #Classe cliente com as suas respectivas informações de nome, porta e ip
    def __init__(self, server_host, server_port, name, password, reception_port = ''):
        self._name = name
        self._ip = socket.gethostbyname(socket.gethostname())
        self._reception_port = reception_port
        self._password = password
        addr = (server_host, server_port) #criação do par ip-porta do servidor
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criação do socket tcp do cliente
        self._socket.connect(addr) #solicita a conexão com o socket tcp do servidor

        #etapa2
        self._listening_server_name = True
        self._p2p_client = None
        self._p2p_server = P2PServer(self)
        self._used_ports = [reception_port]
        self._clear_console = True
        self._in_call = False

    def add_used_port(self, port):
        self._used_ports.append(port)

    def set_in_call(self, truth_value):
        self._in_call = truth_value

    def set_clear_console(self, truth_value):
        self._clear_console = truth_value

    def set_listening_server_name(self, truth_value):
        self._listening_server_name = truth_value

    def get_used_ports(self):
        return self._used_ports
    
    def send_server_call_msg(self, truth_value):
        msg = f'{CLIENT_SET_IN_CALL}::={self._name},{truth_value}'
        self._socket.send(msg.encode(FORMAT))

    def get_input_windows(self, valid_answers):
        user_input = ''
        print('> ', end='', flush=True)
        while not self._in_call:
            if msvcrt.kbhit():
                char = msvcrt.getch().decode()
                if char == '\r':
                    print('')
                    break
                elif char == '\x08' or char == '\x7f' or char == '\b':  # Botão de apagar
                    if user_input:
                        # Apaga o último caractere digitado
                        user_input = user_input[:-1]
                        # Move o cursor de volta e apaga o caractere na tela
                        print('\b \b', end='', flush=True)
                else:
                    print(f'{char}', end='', flush=True)
                    user_input += char

        user_input = user_input.strip()
        if user_input not in valid_answers and user_input != '':
            print(f'[RESPOSTA INVÁLIDA] As respostas possíveis são: {" ou ".join(valid_answers)}.')
            return self.get_input(valid_answers)
        return user_input

    def get_input_linux(self, valid_answers):
        user_input = ''
        print('> ', end='', flush=True)

        # Configuração do terminal para leitura não bloqueante
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        while not self._in_call:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                char = sys.stdin.read(1)
                if char == '\n':
                    print('')
                    break
                elif char == '\x08' or char == '\x7f' or char == '\b': 
                    if user_input:
                        user_input = user_input[:-1]
                        print('\b \b', end='', flush=True)
                else:
                    print(f'{char}', end='', flush=True)
                    user_input += char

        # Restaurar configurações do terminal
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        user_input = user_input.strip()
        if user_input not in valid_answers and user_input != '':
            print(f'[RESPOSTA INVÁLIDA] As respostas possíveis são: {" ou ".join(valid_answers)}.')
            return self.get_input(valid_answers)

        return user_input

    def get_input(self, valid_answers):
        return self.get_input_windows(valid_answers) if os.name == 'nt' else self.get_input_linux(valid_answers)

    def encode_message(self, message): #função que cria a mensagem associada à opção escolhida no menu para ser enviada ao servidor
        if message == '1':
            message = f'{USER_QUERY_MSG}::='
            message += input(f'Insira o usuário a ser buscado> ')

        elif message == '2':
            message = f'{UPDATE_MSG}::={self._name},'
            port = Util.get_port_input(self._used_ports, 'Insira a sua nova porta')
            message += str(port)

        elif message == '3':
            message = f'{USER_QUERY_MSG}::='
            message += input('Insira o nome de para quem deseja ligar> ')

        elif message == '4':
            message = f'{DISCONNECT_MSG}::={self._name}'

        return message
    
    def get_call_ports(self):
        print('\nInforme a porta para receber os fluxos de áudio:')
        audio_port = Util.get_port_input(self._used_ports)
        self._used_ports.append(str(audio_port))

        print('Informe a porta para receber os fluxos de vídeo:')
        video_port =  Util.get_port_input(self._used_ports)
        self._used_ports.append(str(video_port))

        return [audio_port, video_port]
    
    def compute_user_query_call(self, message, valid_answers):
        call_answer = input('> ')
        call_answer = Util.process_input(call_answer, valid_answers)
        if call_answer == 's':
            peer_name, peer_ip, peer_port = message.split('|')
            peer_name = peer_name.split(':')[1].strip()
            peer_ip = peer_ip.split(':')[1].strip()
            peer_port = peer_port.split(':')[1].strip()

            self._listening_server_name = False
            msg = f'{CLIENT_SET_IN_CALL}::={self._name},{True}'
            self._socket.send(msg.encode(FORMAT))

            audio_port, video_port = self.get_call_ports()
            self._p2p_client = P2PClient(self)
            self._p2p_client.start(peer_name, peer_ip, peer_port, self._ip, self._name, audio_port, video_port)
            print('Iniciando requisição...')


    def update_reception_port(self, old_port, new_port):
        self._used_ports.remove(old_port)
        self._used_ports.append(new_port)
        self._p2p_server.set_stop(True)
        time.sleep(1.0)
        self._listening_server_name = False
        server_p2p_thread = threading.Thread(target=self._p2p_server.update_p2p_socket, args=(self._ip, new_port))
        server_p2p_thread.start()
    
    def start_p2p_server_thread(self, ip, port):
        self._listening_server_name = False
        server_p2p_thread = threading.Thread(target=self._p2p_server.start, args=(ip, port))
        server_p2p_thread.start()

    def print_menu(self):
        print('-' * 50)
        print('\'1\' - Realizar consulta por nome de usuário')
        print('\'2\' - Atualizar sua porta de recepção')
        print('\'3\' - Iniciar ligação')
        print('\'4\' - Desvincular-se do servidor' )
        print('-' * 50)

    def establish_server_names_connection(self, option):
        if option == '1':  #verifica se a opção escolhida foi a opção de cadastro  
            msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port},{self._password}' #mensagem de registro 
            self.start_p2p_server_thread(self._ip, self._reception_port)
        else: #se não for, ele solicitou o login
            msg = f'{LOGIN}::={self._name},{self._password}'
        self._socket.send(msg.encode(FORMAT)) #função que envia a mensagem de registro para o servidor

    def run(self, option):
        self.establish_server_names_connection(option)

        receiving = True
        connected = True
        while connected:
            if self._listening_server_name:
                if self._clear_console:
                    Util.clear_console()
                else:
                    self._clear_console = True
                
                if receiving:
                    msg = self._socket.recv(SIZE).decode(FORMAT) #função que fica ouvindo o servidor 
                    msg = Util.split_message(msg) 
                    if len(msg[1].split(',')) == 1:
                        print(f'[SERVIDOR DE NOMES]: {msg[1]}')
                else:
                    msg = '[MENU]::='
                    msg = Util.split_message(msg)
                    receiving = True
                
           
                if msg[0] == LOGIN:
                    print('Bem vindo/a novamente!')
                    reception_port = msg[1]
                    self.start_p2p_server_thread(self._ip, reception_port)
                    self._used_ports.append(reception_port)
                    receiving = False

                elif msg[0] == DISCONNECT_MSG: #se receber uma mensagem do servidor que a conexão foi encerrada, ele sai do loop
                    self._p2p_server.set_stop(True)
                    connected = False
                
                elif msg[0] == FORCED_DISCONNECTION_MSG: #se receber uma mensagem de desconexão forçada, o cliente manda mensagem confirmando a desconexão 
                    msg = f'{FORCED_DISCONNECTION_MSG}::={self._name}'
                    self._socket.send(msg.encode(FORMAT)) 
                    self._p2p_server.set_stop(True)
                    connected = False

                elif msg[0] == TRY_AGAIN or msg[0] == UPDATE_MSG: #tratamento de erro se o usuario digitar uma porta que já existe na tabela no momento do cadastro ou no momento de atualizar sua porta
                    port = Util.get_port_input(self._used_ports, 'Insira a sua porta')
                    self._reception_port = port

                    if(msg[0] == TRY_AGAIN): #nesse caso seria no momento do cadastro
                        msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port},{self._password}'
                    else: #nesse caso seria no momento de atualizar a porta, depois de logado
                        msg = f'{UPDATE_MSG}::={self._name},{self._reception_port}'
                    
                    self._socket.send(msg.encode(FORMAT)) 

                elif msg[0] == USER_QUERY_MSG:
                    content = msg[1]
                    if content.split(':')[0] != USER_NOT_FOUND_MSG: 
                        print('Deseja ligar para este usuário?\n \'s\' - sim\n \'n\' - não')
                        self.compute_user_query_call(content, ['s', 'n'])

                    else:
                        self._clear_console = False
                    receiving = False

                elif msg[0] == UPDATE_ACK:
                    print('Sua porta foi atualizada com sucesso!')
                    old_port, new_port = msg[1].split(',')
                    self.update_reception_port(old_port, new_port)
                    self._clear_console = False
                    receiving = False

                else:
                    self.print_menu()
                    msg = self.get_input(['1', '2', '3', '4'])
                    if msg == '':
                        receiving = False
                        continue
                    msg = self.encode_message(msg)
                    self._socket.send(msg.encode(FORMAT))

        self._socket.close() #função que fecha o socket e finaliza o processo do cliente

def main():
    print('-' * 50)
    print('\'1\' - Realizar cadastro')
    print('\'2\' - Realizar login')
    print('-' * 50)
    option = input('> ')
    option = Util.process_input(option, ['1', '2'])

    if option == '1':
        name = input('Insira seu nome> ')
        name = Util.process_open_input('Insira seu nome', name)
        port = Util.get_port_input([], 'Insira a sua porta')
        password = getpass.getpass('Insira sua senha a ser cadastrada: ')
        
        client = Client(ip_server, server_port, name, password, str(port))
    else:
        name = input('Insira seu nome> ')
        name = Util.process_open_input('Insira seu nome', name)
        password = getpass.getpass('Insira a sua senha> ')
        
        client = Client(ip_server, server_port, name, password)

    client.run(option)


if __name__ == "__main__":
    main()
        