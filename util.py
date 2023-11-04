import os

class Util:
    def get_port_input():
        port = int(input(f'Insira a sua porta> '))
        while(port < 1025 or port > 65535):
            print("Porta inválida, tente novamente (1025 até 65535).")
            port = int(input(f'Insira a sua porta> '))
        
        return port
    
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')