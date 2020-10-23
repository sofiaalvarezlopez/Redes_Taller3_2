import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverAddress = ('localhost', 10000)
message = b'Is this the real laif'
buffer = 1024

try:
    print('enviado datos {}'.format(message))
    sent = sock.sendto(message, serverAddress)

    data, address = sock.recvfrom(buffer)
    print ("Received File:",data.strip())
    f = open('./Cliente/' + repr(data.strip())[2:-1],"wb")

    data, address = sock.recvfrom(buffer)

    while data:
        f.write(data)
        data,addr = sock.recvfrom(buffer)
    f.close()
finally:
    sock.close()