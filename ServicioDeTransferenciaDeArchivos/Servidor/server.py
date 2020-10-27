import socket
import os
from threading import Thread
from socketserver import ThreadingMixIn
from ClientHandler import ClientHandler
import datetime

path = './Servidor/files/'
log_path = './Servidor/logs/'
files = os.listdir(path)
try:
    files.remove('.DS_Store')
except:
    pass

numClientes = int(input('Indique el numero maximo de clientes a conectar: '))
print('Los archivos disponibles en el servidor son: ')

for i in range(len(files)):
    print(str(i+1) + '. ' + files[i]) 

j = 0
try:
    j = int(input('Escoja el numero de archivo a enviar: \n')) - 1
except:
    print('Opcion incorrecta.')
    tcpsock.close()
    exit()

filename = files[j]
fechaPrueba = str(datetime.datetime.now())
log = open(log_path + fechaPrueba + '.log', 'w')
log.write('Fecha y Hora: ' + fechaPrueba + '\n')
log.write('Nombre Archivo: ' + filename + '\n')
log.write('Tamaño Archivo: ' + str(os.path.getsize(path + filename)) + '\n' )

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
buffer = 1024

EC2_PUBLIC_IP = '54.226.145.99'
UDP_IP = socket.gethostbyaddr(EC2_PUBLIC_IP)[0]
#UDP_IP = 'localhost'
serverAddress = (UDP_IP, 10000)
sock.bind(serverAddress)
threads = []

for i in range(numClientes):
    print('Esperando mensaje')
    data, address = sock.recvfrom(buffer)
    print('se recibio conexion de {} con la informacion {}'.format(address, data))
    newThread = ClientHandler(address, sock, path + filename, log)
    threads.append(newThread)

for t in threads:
    t.start()
sock.close()
