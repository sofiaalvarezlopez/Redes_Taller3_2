import socket
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverAddress = ('localhost', 10000)
buffer = 1024
sock.bind(serverAddress)


filename = './Servidor/prueba.txt'

f = open(filename, 'rb')

print('Esperando mensaje')
data, address = sock.recvfrom(buffer)


data = f.read(buffer)
sock.sendto(filename[11:].encode(), address)
sock.sendto(data, address)

while data:
    if(sock.sendto(data,address)):
        print ("sending ...")
    data = f.read(buffer)

sock.close()
f.close()