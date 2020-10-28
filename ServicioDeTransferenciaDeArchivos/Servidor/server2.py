import socket
import os
from threading import Thread
from socketserver import ThreadingMixIn
from ClientHandler2 import ClientHandler
import datetime

#Ruta donde se encuentran los archivos en el servidor
path = './Servidor/files/'
#Ruta donde se almacenan los logs en el servidor
log_path = './Servidor/logs/'
#Se listan los archivos que hay en el servidor
files = os.listdir(path)
try:
    files.remove('.DS_Store')
except:
    pass
#Se pide al cliente indicar el numero maximo de clientes a conectar
numClientes = int(input('Indique el numero maximo de clientes a conectar: '))
print('Los archivos disponibles en el servidor son: ')
#Se listan los archivos
for i in range(len(files)):
    print(str(i+1) + '. ' + files[i]) 

#Se pide al cliente que escoja el numero del archivo que desea
j = 0
try:
    j = int(input('Escoja el numero de archivo a enviar: \n')) - 1
except:
    print('Opcion incorrecta.')
    tcpsock.close()
    exit()

filename = files[j]
#Se imprimen la fecha en que se realizo la prueba, asi como el nombre y tamanio del archivo.
fechaPrueba = str(datetime.datetime.now())
log = open(log_path + fechaPrueba + '.log', 'w')
log.write('Fecha y Hora: ' + fechaPrueba + '\n')
log.write('Nombre Archivo: ' + filename + '\n')
log.write('Tamaño Archivo: ' + str(os.path.getsize(path + filename)) + '\n' )

#Se crea un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#Se define el tamanio que tendra el buffer
BUFFER = 1024

#IP donde corre el servidor. Si no es en la nube o en una MV, usar localhost para correr localmente.
EC2_PUBLIC_IP = '54.226.145.99'
UDP_IP = socket.gethostbyaddr(EC2_PUBLIC_IP)[0]
UDP_IP = 'localhost'
serverAddress = (UDP_IP, 10000)
sock.bind(serverAddress)
threads = {}
#Creamos un thread para manejar las peticiones de cada cliente.
for i in range(numClientes):
    print('Esperando mensaje')
    data, address = sock.recvfrom(BUFFER)
    print('se recibio conexion de {} con la informacion {}'.format(address, data))
    newThread = ClientHandler(address, sock, path + filename, log)
    threads[address] = newThread

for t in threads:
    threads[t].start()
while True:
    data, address = sock.recvfrom(BUFFER)
    if address in threads:
        threads[address].changeState(data)

sock.close()
