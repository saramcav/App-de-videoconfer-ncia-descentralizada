import socket
host = socket.gethostbyname(socket.gethostname())
port = 5000

SIZE = 1024
FORMAT = 'utf-8'
DISCONNECT_MSG = '[DISCONNECT]'
NEW_REGISTER_MSG = '[REGISTER]'
USER_QUERY_MSG = '[USER_QUERY]'