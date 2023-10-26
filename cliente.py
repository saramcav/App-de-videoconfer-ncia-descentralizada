import socket 
from utils import *

class Client:
    #Classe cliente com as suas respectivas informações de nome, porta e ip
    def __init__(self, server_host, server_port, name, ip, reception_port):
        self._name = name
        self._ip = ip
        self._reception_port = reception_port
        addr = (server_host, server_port) #criação do par ip-porta do servidor
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criação do socket tcp do cliente
        self._socket.connect(addr) #solicita a conexão com o socket tcp do servidor
        print(f'[CONEXAO] cliente conectado ao servidor em {server_host}:{server_port}\n')
        self.run()

    def encode_message(self, message): #função que cria a mensagem associada à opção escolhida no menu para ser enviada ao servidor
        if message == '1':
            message = f'{USER_QUERY_MSG}::='
            message += str(input(f'Insira o usuário a ser buscado> '))
            
        elif message == '2':
            message = f'{DISCONNECT_MSG}::={self._name}'

        elif message == '3':
            message = f'{TABLE_QUERY_MSG}::={self._name}' 

        return message

    def decode_message(self, message): #função para decodificar uma mensagem recebida do servidor
        msg = message.split("::=")
        return msg
    
    def run(self):    
        msg = f'{NEW_REGISTER_MSG}::={self._name},{self._ip},{self._reception_port}' #mensagem de registro 
        self._socket.send(msg.encode(FORMAT)) #função que envia a mensagem de registro para o servidor

        print('Para realizar uma consulta pelo nome de usuário, insira \'1\'')
        print('Para se desvincular do servidor, insira \'2\'')
        print('Para consultar a tabela de clientes conectados no servidor, insira \'3\'\n')

        conectado = True
        while conectado:
            msg = self._socket.recv(SIZE).decode(FORMAT) #função que fica ouvindo o servidor 
            msg = self.decode_message(msg) 
            print(f'[SERVIDOR]: {msg[1]}')

            if msg[0] == DISCONNECT_MSG: #se receber uma mensagem do servidor que a conexão foi encerrada, ele sai do loop
                conectado = False

            else:
                msg = str(input(f'> ')) #input para a escolha das mensagens que são enviadas ao servidor
                msg = self.encode_message(msg)
                self._socket.send(msg.encode(FORMAT))  #função que envia a mensagem de registro para o servidor

        self._socket.close() #função que fecha o socket e finaliza o processo do cliente

def main():
    nome = str(input(f'Insira o seu nome> '))
    endereco = str(input(f'Insira o seu endereço de IP> '))
    porta = str(input(f'Insira a sua porta> '))

    cliente = Client(host, port, nome, endereco, porta)


if __name__ == "__main__":
    main()
        