import os

class Util:
    def get_port_input(used_ports, label=''):
        while True:
            try:
                port = int(input(f'{label}> '))
                if port < 1025 or port > 65535:
                    print('[PORTA INVÁLIDA] Tente novamente (1025 até 65535).')
                    continue
                
                if str(port) in used_ports:
                    print(f'[PORTA INVÁLIDA] Use uma porta diferente de {", ".join(used_ports)}.')
                    continue
                
                return port  

            except ValueError:
                print('[VALOR INVÁLIDO] Insira um número inteiro válido.')
                

    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    
    def process_input(text, valid_answers):
        valid = True
        text = text.strip().lower()

        if text == '':
            print('[RESPOSTA INVÁLIDA] Preencha a entrada.')
            valid = False

        elif text not in valid_answers:
            print(f'[RESPOSTA INVÁLIDA] As respostas possíveis são: {" ou ".join(valid_answers)}.')
            valid = False
        
        if not valid: 
            text = input('> ')
            return Util.process_input(text, valid_answers)
        return text
    
    def process_open_input(label, text):
        text = text.strip().lower()
        valid = True

        if text == '':
            print('[RESPOSTA INVÁLIDA] Preencha a entrada.')
            valid = False
        
        if not valid:
            text = input(f'{label}> ')
            return Util.process_open_input(label, text)
        return text
    
    def split_message(message): #função para decodificar uma mensagem recebida do servidor
        msg = message.split("::=")
        return msg