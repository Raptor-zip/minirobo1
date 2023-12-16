import socket
M_SIZE = 1024
sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
sock.bind(('127.0.0.1',5002))

while True:
    try :
        message, cli_addr = sock.recvfrom(M_SIZE)
        message = message.decode(encoding='utf-8')
        print(f'Received message : {message}')
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()
        break