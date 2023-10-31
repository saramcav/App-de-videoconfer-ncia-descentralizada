import socket
import threading
from utils import *

class ClientRegister:
    def __init__(self, ip, reception_port, online):
        self._ip = ip
        self._reception_port = reception_port
        self._online = online
    
    def get_ip(self):
        return self._ip

    def get_reception_port(self):
        return self._reception_port
    
    def get_status(self):
        return self._online

    def set_status(self, online):
        self._online = online 

    def set_reception_port(self, reception_port):
        self._reception_port = reception_port


class Server:
    def __init__(self, host, port):
        self._clients = {} #dicinário com os registros de clientes
        addr = (host, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criação do socket tcp do servidor
        self._socket.bind(addr) #vincula um par ip-porta para o socket do servidor
        self._socket.listen() #servidor fica escutando as solicitações dos clientes
        print(f'O servidor está ouvindo em {host}:{port}')
    
    def run(self):
        while True:
            conn, addr = self._socket.accept() #aceita a conexão de acordo com o endereço do cliente
            thread = threading.Thread(target=self.handle_client, args=(conn, addr)) #cria uma thread para esse cliente
            thread.start()
            print(f'[CONEXOES ATIVAS] {threading.active_count() - 1}')
    
    def handle_client(self, conn, addr):
        conectado = True
        while conectado:
            msg = conn.recv(SIZE).decode(FORMAT) #função que fica ouvindo o socket cliente
            print(f'[{addr}] {msg}')
            msg = self.split_message(msg)

            if msg[0] == DISCONNECT_MSG: #se a mensagem recebida for para desconectar o cliente
                client = msg[1]
                print(f'[CLIENTE DESCONECTADO] {client} deixou o servidor ...')
                print(f'[CONEXOES ATIVAS] {threading.active_count() - 2}')
                msg = f'{DISCONNECT_MSG}::=VOCÊ FOI DESCONECTADO/A!' #mensagem de retorno para o cliente
                self._clients[client].set_status(False)
                conectado = False #torna variável = false para poder sair do loop
                print(self.clients_table())
            
            elif msg[0] == FORCED_DISCONNECTION_MSG: #mensagem de confirmação da desconexão forçada enviada pelo cliente
                client = msg[1]
                print(f'[CONEXÃO JÁ EXISTENTE] Fechando conexão do/a {client}...')
                conectado = False
                break

            elif msg[0] == NEW_REGISTER_MSG: #se a mensagem recebida for de um novo registro
                name, ip, reception_port = msg[1].split(',')
                msg = self.add_client_register(name, ip, reception_port) #mensagem de retorno para o cliente
                print(self.clients_table()) #printa a tabela de clientes
            
            elif msg[0] == USER_QUERY_MSG: #se a mensagem recebida for uma busca de outro usuário
                name = msg[1]
                msg = f'{USER_QUERY_MSG}::={self.query_user(name)}' #mensagem de retorno para o cliente

            else:
                msg = f'{WRONG_OPTION}::=OPÇÃO INVÁLIDA' #mensagem de retorno para o cliente
            
            conn.send(msg.encode(FORMAT)) #função que envia a mensagem resposta para o cliente
            
        conn.close() #função que encerra a conexão com o socket cliente
    
    
    def split_message(self, message): #função para decodificar uma mensagem recebida do cliente
        msg = message.split("::=")
        return msg
        
            
    def add_client_register(self, name, ip, reception_port): #função que adiciona um novo registro de cliente no servidor e retorna uma mensagem
        client_register = self._clients.get(name) #procura na tabela se já existe o nome de usuário igual ao informado
        client_addr = None
        for client in self._clients.values(): #procura na tabela se já existe algum par IP-Porta igual ao informado
                if client.get_ip() == ip and client.get_reception_port() == reception_port:
                    client_addr = client

        if client_register is None: #caso o nome informado não esteja na tabela
            if client_addr is None: #caso o par IP-Porta não esteja na tabela, o servidor adiciona o novo registro na tabela
                self._clients[name] = ClientRegister(ip, reception_port, True)
                msg = f'{REGISTRATION_SUCCESS_MSG}::={name} Cadastro realizado! Bem vindo/a!'
            else: #caso o par IP-Porta já exista na tabela, o servidor não adiciona o registro e força a desconexão com o cliente
                msg = f'{FORCED_DISCONNECTION_MSG}::=Já existe uma conexão referente a esse par Ip-Porta!'
        elif client_register.get_status() == True: #caso exista o nome na tabela e ele está online, o servidor força a desconexão
            msg = f'{FORCED_DISCONNECTION_MSG}::=Já existe uma conexão aberta para esse cliente!'
        else: #caso exista o nome na tabela e ele está offline, o servidor atualiza a porta, caso ela seja diferente da registrada anteriormente
            msg = f'{REGISTRATION_FAILED_MSG}::=Você já está cadastrado/a. Bem vindo/a novamente!' 
            if(client_register.get_reception_port() != reception_port):
                client_register.set_reception_port(reception_port) 
                msg += ' Sua porta foi atualizada com sucesso!'
            client_register.set_status(True)

        return msg

    def query_user(self, client_name): #função que busca um nome de usuário solicitado pelo cliente e retorna uma mensagem
        client = self._clients.get(client_name)

        if client is None:
            msg = f'{USER_NOT_FOUND_MSG} O usuário informado não existe!'
        elif client.get_status() == False:
            msg = f'{USER_NOT_FOUND_MSG} O usuário não está online no momento!'
        else:
            msg = f'NOME: {client_name:<12} | IP: {client.get_ip():<20} | RECEPTION_PORT: {client.get_reception_port():<6}'
        return msg
    
    def clients_table(self): #função que retorna a tabela de todos os clientes conectados no servidor como mensagem
        msg = f'{"NOME":<12} | {"IP":<20} | {"PORTA":<6} | {"ONLINE":<4}\n'
        msg += '-' * 60 + '\n'
        for name in self._clients:
            status = 'NÃO'
            client = self._clients.get(name)
            if client.get_status() == True: #verifica se o cliente está online ou não para poder printar o status corretamente
                status = 'SIM'
            msg += f'{name:<12} | {client.get_ip():<20} | {client.get_reception_port():<6} | {status:<4}\n'
            msg += '-' * 60 + '\n'
        return msg

def main(): 
    s = Server(ip_server, server_port) 
    s.run() 
 
if __name__ == "__main__": 
    main()