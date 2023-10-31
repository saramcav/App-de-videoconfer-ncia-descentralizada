import socket
from utils import *

class Client:
    #Classe cliente com as suas respectivas informações de nome, porta e ip
    def __init__(self, server_host, server_port, name, reception_port):
        self._name = name
        self._ip = socket.gethostbyname(socket.gethostname())
        self._reception_port = reception_port
        addr = (server_host, server_port) #criação do par ip-porta do servidor
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criação do socket tcp do cliente
        self._socket.connect(addr) #solicita a conexão com o socket tcp do servidor

    def encode_message(self, message): #função que cria a mensagem associada à opção escolhida no menu para ser enviada ao servidor
        if message == '1':
            message = f'{USER_QUERY_MSG}::='
            message += str(input(f'Insira o usuário a ser buscado> '))
            
        elif message == '2':
            message = f'{DISCONNECT_MSG}::={self._name}'

        return message

    def split_message(self, message): #função para decodificar uma mensagem recebida do servidor
        msg = message.split("::=")
        return msg
    
    def run(self):    
        msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port}' #mensagem de registro 
        self._socket.send(msg.encode(FORMAT)) #função que envia a mensagem de registro para o servidor

        print('Para realizar uma consulta pelo nome de usuário, insira \'1\'')
        print('Para se desvincular do servidor, insira \'2\'')

        conectado = True
        while conectado:
            msg = self._socket.recv(SIZE).decode(FORMAT) #função que fica ouvindo o servidor 
            msg = self.split_message(msg) 
            print(f'[SERVIDOR]: {msg[1]}')

            if msg[0] == DISCONNECT_MSG: #se receber uma mensagem do servidor que a conexão foi encerrada, ele sai do loop
                conectado = False
            
            elif msg[0] == FORCED_DISCONNECTION_MSG: #se receber uma mensagem de desconexão forçada, o cliente manda mensagem confirmando a desconexão 
                msg = f'{FORCED_DISCONNECTION_MSG}::={self._name}'
                self._socket.send(msg.encode(FORMAT)) 
                conectado = False
            
            else:
                msg = str(input(f'> ')) #input para a escolha das mensagens que são enviadas ao servidor
                msg = self.encode_message(msg)
                self._socket.send(msg.encode(FORMAT))  #função que envia a mensagem de registro para o servidor

        self._socket.close() #função que fecha o socket e finaliza o processo do cliente

   
def main():
    nome = str(input(f'Insira o seu nome> '))
    porta = int(input(f'Insira a sua porta> '))
    while(porta < 1025 or porta > 65535): #vericação para o cliente digitar uma porta correta
        print("Porta inválida, tente novamente (1025 até 65535).")
        porta = int(input(f'Insira a sua porta> '))
    
    cliente = Client(ip_server, server_port, nome, str(porta))
    cliente.run()


if __name__ == "__main__":
    main()
        