import os
import socket
import getpass
from utils import *

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

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def encode_message(self, message): #função que cria a mensagem associada à opção escolhida no menu para ser enviada ao servidor
        if message == '1':
            message = f'{USER_QUERY_MSG}::='
            message += str(input(f'Insira o usuário a ser buscado> '))

        elif message == '2':
            message = f'{UPDATE_MSG}::={self._name},'
            port = int(input('Indique sua nova porta de recepção> '))
            while(port < 1025 or port > 65535): #vericação para o cliente digitar uma porta correta
                print("Porta inválida, tente novamente (1025 até 65535).")
                port = int(input('Indique sua nova porta de recepção> '))
            message += str(port)

        elif message == '3':
            message = f'{DISCONNECT_MSG}::={self._name}'

        return message


    def split_message(self, message): #função para decodificar uma mensagem recebida do servidor
        msg = message.split("::=")
        return msg
    
    def run(self, option):
        if option == 1:  #verifica se a opção escolhida foi a opção de cadastro  
            msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port},{self._password}' #mensagem de registro 
        else: #se não for, ele solicitou o login
            msg = f'{LOGIN}::={self._name},{self._password}'

        self._socket.send(msg.encode(FORMAT)) #função que envia a mensagem de registro para o servidor

        conectado = True
        while conectado:
            self.clear_console() #função para limpar o console
            msg = self._socket.recv(SIZE).decode(FORMAT) #função que fica ouvindo o servidor 
            msg = self.split_message(msg) 
            print(f'[SERVIDOR]: {msg[1]}')

            if msg[0] == DISCONNECT_MSG: #se receber uma mensagem do servidor que a conexão foi encerrada, ele sai do loop
                conectado = False
            
            elif msg[0] == FORCED_DISCONNECTION_MSG: #se receber uma mensagem de desconexão forçada, o cliente manda mensagem confirmando a desconexão 
                msg = f'{FORCED_DISCONNECTION_MSG}::={self._name}'
                self._socket.send(msg.encode(FORMAT)) 
                conectado = False

            elif msg[0] == TRY_AGAIN or msg[0] == UPDATE_MSG: #tratamento de erro se o usuario digitar uma porta que já existe na tabela no momento do cadastro ou no momento de atualizar sua porta
                port = int(input(f'Insira a sua porta> '))
                while(port < 1025 or port > 65535): #vericação para o cliente digitar uma porta correta
                    print("Porta inválida, tente novamente (1025 até 65535).")
                    port = int(input(f'Insira a sua porta> '))
                self._reception_port = port

                if(msg[0] == TRY_AGAIN): #nesse caso seria no momento do cadastro
                    msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port},{self._password}'
                else: #nesse caso seria no momento de atualizar a porta, depois de logado
                    msg = f'{UPDATE_MSG}::={self._name},{self._reception_port}'
                
                self._socket.send(msg.encode(FORMAT)) 

            
            else:
                print('-' * 50)
                print('\'1\' - Realizar consulta por nome de usuário')
                print('\'2\' - Atualizar sua porta de recepção')
                print('\'3\' - Desvincular-se do servidor')
                print("-" * 50)
                msg = str(input(f'> ')) #input para a escolha das mensagens que são enviadas ao servidor
                msg = self.encode_message(msg)
                self._socket.send(msg.encode(FORMAT))  #função que envia a mensagem de registro para o servidor

        self._socket.close() #função que fecha o socket e finaliza o processo do cliente

def main():
    print('-' * 50)
    print('\'1\' - Realizar cadastro')
    print('\'2\' - Realizar login')
    print('-' * 50)
    option = int(input('> '))

    while option < 1 or option > 2: #vericação para o cliente digitar uma opcao correta
        print('Escolha entre 1 ou 2!')
        option = int(input('> '))

    if option == 1:
        name = str(input(f'Insira o seu nome> '))
        port = int(input(f'Insira a sua porta> '))
        while(port < 1025 or port > 65535): #vericação para o cliente digitar uma porta correta
            print("Porta inválida, tente novamente (1025 até 65535).")
            port = int(input(f'Insira a sua porta> '))

        password = getpass.getpass('Insira sua senha a ser cadastrada: ')
        client = Client(ip_server, server_port, name, str(port), password)
    else:
        name = str(input(f'Insira o seu nome> '))
        password = getpass.getpass('Insira a sua senha> ')
        client = Client(ip_server, server_port, name, '', password)
    client.run(option)


if __name__ == "__main__":
    main()
        