import socket
import threading
from config import *
from client_register import ClientRegister

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
                self._clients[client].set_online_status(False)
                conectado = False #torna variável = false para poder sair do loop
                print(self.clients_table())
            
            elif msg[0] == FORCED_DISCONNECTION_MSG: #mensagem de confirmação da desconexão forçada enviada pelo cliente
                client = msg[1]
                print(f'[CONEXÃO JÁ EXISTENTE] Fechando conexão do/a {client}...')
                conectado = False
                break

            elif msg[0] == NEW_REGISTER_MSG: #se a mensagem recebida for de um novo registro
                name, ip, reception_port, password = msg[1].split(',')
                msg = self.add_client_register(name, ip, reception_port, password) #mensagem de retorno para o cliente
                print(self.clients_table()) #printa a tabela de clientes

            elif msg[0] == LOGIN: #se a mensagem recebida for a de login
                name, password = msg[1].split(',')
                msg = self.validate_login(name, password) #função para validar se a senha está correta e se existe o usuário
                print(self.clients_table())    

            elif msg[0] == USER_QUERY_MSG: #se a mensagem recebida for uma busca de outro usuário
                name = msg[1]
                msg = f'{USER_QUERY_MSG}::={self.query_user(name)}' #mensagem de retorno para o cliente

            elif msg[0] == UPDATE_MSG: #se a mensagem recebida foi a de atualizar o número de porta
                name, new_port = msg[1].split(',')
                msg = self.update_client_register(name, new_port) #função que verifica e atualiza a porta
                print(self.clients_table())

            else:
                msg = f'{WRONG_OPTION}::=OPÇÃO INVÁLIDA' #mensagem de retorno para o cliente
            
            conn.send(msg.encode(FORMAT)) #função que envia a mensagem resposta para o cliente
            
        conn.close() #função que encerra a conexão com o socket cliente
    
    def split_message(self, message): #função para decodificar uma mensagem recebida do cliente
        msg = message.split("::=")
        return msg

    def validate_login(self, name, password):
        client_register = self._clients.get(name)
        if client_register is not None: #valida se o cliente existe
            is_valid_login = self.validate_password(client_register, password)
            if is_valid_login: #valida se a senha digitada é a mesma guardada no dicionário
                if client_register.get_status() == True: #caso exista o nome na tabela e ele está online, o servidor força a desconexão
                    msg = f'{FORCED_DISCONNECTION_MSG}::=Já existe uma conexão aberta para esse cliente!'
                else: #se não estiver online, o cliente entra com sucesso no servidor
                    msg = f'{LOGIN}::=Bem vindo/a novamente!'
                    client_register.set_online_status(True)
            else: #se não for, ele retorna uma mensagem de senha inválida, além de desconectar o cliente do servidor
                msg = f'{FORCED_DISCONNECTION_MSG}::=Senha inválida. Você será desconectado...'
        else:
            msg = f'{FORCED_DISCONNECTION_MSG}::=Este cliente não existe. Você será desconectado...'
        
        return msg

    def validate_password(self, client_register, password):
        if client_register.get_password() != password:
            return False
        return True

    def update_client_register(self, name, new_port):
        client_addr = None
        for client in self._clients.values(): #procura na tabela se já existe algum par IP-Porta igual ao informado
                if client.get_reception_port() == new_port:
                    client_addr = client

        if client_addr is None: #se não existe, é porque a porta informada não existe na tabela e pode ser utilizada
            msg = f'{UPDATE_ACK}::=Sua porta foi atualizada com sucesso!'
            client_register = self._clients.get(name)
            client_register.set_reception_port(new_port)
            client_register.set_online_status(True)
        else:
            msg = f'{UPDATE_MSG}::=Já existe um registro utilizando esse par IP-Porta! Tente novamente com outra porta!'

        return msg

    def add_client_register(self, name, ip, reception_port, password): #função que adiciona um novo registro de cliente no servidor e retorna uma mensagem
        client_register = self._clients.get(name) #procura na tabela se já existe o nome de usuário igual ao informado
        client_addr = None
        for client in self._clients.values(): #procura na tabela se já existe algum par IP-Porta igual ao informado
                if client.get_ip() == ip and client.get_reception_port() == reception_port:
                    client_addr = client

        if client_register is None: #caso o nome informado não esteja na tabela
            if client_addr is None: #caso o par IP-Porta não esteja na tabela, o servidor adiciona o novo registro na tabela
                self._clients[name] = ClientRegister(ip, reception_port, password, True)
                msg = f'{REGISTRATION_SUCCESS_MSG}::=Cadastro realizado! Bem vindo/a, {name}!'
            else: #caso o par IP-Porta já exista na tabela, o servidor não adiciona o registro e força a desconexão com o cliente
                msg = f'{TRY_AGAIN}::=Já existe um registro utilizando esse par IP-Porta! Tente novamente com outra porta!'
        else:
            msg = f'{FORCED_DISCONNECTION_MSG}::=Já existe um cadastro com este nome!'

        return msg

    def query_user(self, client_name): #função que busca um nome de usuário solicitado pelo cliente e retorna uma mensagem
        client = self._clients.get(client_name)

        if client is None:
            msg = f'{USER_NOT_FOUND_MSG}: O usuário informado não existe!'
        elif client.get_status() == False:
            msg = f'{USER_NOT_FOUND_MSG}: O usuário não está online no momento!'
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