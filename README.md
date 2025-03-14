# Trabalho de Redes de Computadores II

# Aplicação de Videoconferência Descentralizada

## Descrição

Esta aplicação implementa uma solução de videoconferência descentralizada utilizando comunicação por sockets. O sistema permite que usuários se registrem em um servidor central, consultem a lista de nós cadastrados e estabeleçam conexões diretas Peer-to-Peer (P2P) para comunicação de áudio e vídeo.

## Funcionalidades

### Registro e Consulta no Servidor
- Os clientes podem se registrar no servidor informando um nome único, IP e porta para receber chamadas.
- O servidor mantém uma tabela dinâmica com os usuários conectados e exibe mensagens de confirmação ao registrar novos clientes.
- Os clientes podem consultar a lista de usuários registrados e obter os endereços IP e portas de outros participantes.
- Caso um usuário já esteja cadastrado, o servidor informa essa condição.
- Os clientes podem solicitar a remoção do registro, encerrando sua conexão com o servidor.
- O servidor responde com uma mensagem de encerramento quando um cliente desconecta.

### Implementação do Serviço
- Os clientes podem solicitar videochamadas para outros usuários através de um protocolo de convite semelhante ao SIP.
- O destinatário da chamada pode aceitar ou recusar a solicitação.
- Caso a chamada seja aceita, os fluxos de áudio e vídeo são iniciados automaticamente.
- O servidor gerencia as chamadas, fornecendo informações sobre as portas utilizadas para transmissão.
- A aplicação conta com métodos para encerramento da transmissão e desconexão dos usuários.

## Passos para rodar a aplicação 
1. Clone o repositório: <br/>
`~$ git clone https://github.com/SerranoZz/trabalho-redes2.git`

2. Vá para o diretório do projeto:<br/>
`~$ cd trabalho-redes2`

3. Execute o código do servidor:<br/>
`~$ python server.py`

5. Execute o código do cliente:<br/>
`~$ python client.py`


## Colaboradores

Este trabalho foi realizado em dupla com o [Lucas Serrano](https://github.com/SerranoZz)
