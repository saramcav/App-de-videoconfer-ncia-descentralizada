import socket
import getpass
import threading
from config import *
from p2p_client import P2PClient
from p2p_server import P2PServer
from util import Util

class Client:
    #Classe cliente com as suas respectivas informações de nome, porta e ip
    def __init__(self, server_host, server_port, name, reception_port, password):
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

        self._rejected_call = False

    def set_rejected_call(self, truth_value):
        self._rejected_call = truth_value

    def set_listening_server_name(self, truth_value):
        self._listening_server_name = truth_value

    def encode_message(self, message): #função que cria a mensagem associada à opção escolhida no menu para ser enviada ao servidor
        if message == '1':
            message = f'{USER_QUERY_MSG}::='
            message += input(f'Insira o usuário a ser buscado> ')

        elif message == '2':
            message = f'{UPDATE_MSG}::={self._name},'
            port = Util.get_port_input('Insira a sua porta')
            message += str(port)

        elif message == '3':
            message = f'{USER_QUERY_MSG}::='
            message += input('Insira o nome de para quem deseja ligar> ')

        elif message == '4':
            message = f'{DISCONNECT_MSG}::={self._name}'

        return message


    def split_message(self, message): #função para decodificar uma mensagem recebida do servidor
        msg = message.split("::=")
        return msg
    
    def compute_user_query_answer(self, message, valid_answers):
        call_answer = input('> ')
        call_answer = Util.process_input(call_answer, valid_answers)
        if call_answer == 's':
            print('Iniciando ligação...')
            _, peer_ip, peer_port = message.split('|')
            peer_ip = peer_ip.split(':')[1].strip()
            peer_port = peer_port.split(':')[1].strip()

            self._p2p_client = P2PClient(self)
            self._listening_server_name = False
            client_p2p_thread = threading.Thread(target=self._p2p_client.start, args=(peer_ip, peer_port, self._name))
            client_p2p_thread.start()
    
    def run(self, option):
        if option == '1':  #verifica se a opção escolhida foi a opção de cadastro  
            msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port},{self._password}' #mensagem de registro 
        else: #se não for, ele solicitou o login
            msg = f'{LOGIN}::={self._name},{self._password}'

        self._socket.send(msg.encode(FORMAT)) #função que envia a mensagem de registro para o servidor

        server_p2p_thread = threading.Thread(target=self._p2p_server.start, args=(self._ip, self._reception_port))
        server_p2p_thread.start()

        receiving = True
        connected = True
        while connected:
            if self._listening_server_name:
                if not self._rejected_call:
                    Util.clear_console()
                else:
                    self.rejected_call = False
                
                if receiving:
                    msg = self._socket.recv(SIZE).decode(FORMAT) #função que fica ouvindo o servidor 
                    msg = self.split_message(msg) 
                    print(f'[SERVIDOR DE NOMES]: {msg[1]}')
                else:
                    msg = '[MENU]::='
                    msg = self.split_message(msg)
                    receiving = True
                

                if msg[0] == DISCONNECT_MSG: #se receber uma mensagem do servidor que a conexão foi encerrada, ele sai do loop
                    connected = False
                
                elif msg[0] == FORCED_DISCONNECTION_MSG: #se receber uma mensagem de desconexão forçada, o cliente manda mensagem confirmando a desconexão 
                    msg = f'{FORCED_DISCONNECTION_MSG}::={self._name}'
                    self._socket.send(msg.encode(FORMAT)) 
                    connected = False

                elif msg[0] == TRY_AGAIN or msg[0] == UPDATE_MSG: #tratamento de erro se o usuario digitar uma porta que já existe na tabela no momento do cadastro ou no momento de atualizar sua porta
                    port = Util.get_port_input('Insira a sua porta')
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
                        self.compute_user_query_answer(content, ['s', 'n'])
                    receiving = False

                else:
                    print('-' * 50)
                    print('\'1\' - Realizar consulta por nome de usuário')
                    print('\'2\' - Atualizar sua porta de recepção')
                    print('\'3\' - Iniciar ligação')
                    print('\'4\' - Desvincular-se do servidor' )
                    print('-' * 50)
                    msg = Util.get_input()
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
        port = Util.get_port_input('Insira a sua porta')
        password = getpass.getpass('Insira sua senha a ser cadastrada: ')
        
        client = Client(ip_server, server_port, name, str(port), password)
    else:
        name = input('Insira seu nome> ')
        name = Util.process_open_input('Insira seu nome', name)
        password = getpass.getpass('Insira a sua senha> ')
        
        client = Client(ip_server, server_port, name, '', password)

    client.run(option)


if __name__ == "__main__":
    main()
        