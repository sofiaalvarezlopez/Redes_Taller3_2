import socket
from threading import Thread
from socketserver import ThreadingMixIn
import struct
import datetime
import os
import hashlib
import sys
from udp_monitor2 import Monitor

#Tamanio del paquete a ser enviado
BUFFER_SIZE = 1024
#Direccion del servidor. Si no se corre en la nube o en una maquina virtual, usar localhost para correr localmente
serverAddress = ('54.226.145.99', 10000)
#serverAddress = ('localhost', 10000)
#Comando que indica que el cliente esta listo para recibir archivos
BEG_RECV = b'BEG_RECV'
RECV = b'RECV'
SEND = b'SEND'
#Comando que indica que el archivo se recibio correctamente 
OK = b'OK'
#Comando que indica que hubo un error en la comunicacion o que el archivo no se recibio adecuadamente
ERR = b'ERR'
#Comando que indica la finalizacion de la transmision del archivo enviado
END_TRANSMISSION = b'END_TRANSMISSION'
#Comando que indica la finalizacion del protocolo
FIN = b'FIN'

class ClientHandler(Thread):
    def __init__(self, address, sock, archivoElegido, log):
        Thread.__init__(self)
        #Direccion del cliente que se esta comunicando
        self.address = address
        #Socket que esta siendo usado por el servidor para comunicarse con el cliente
        self.sock = sock
        #Archivo que se ha elegido en el servidor para ser enviado al cliente
        self.archivoElegido = archivoElegido
        #Log en el que se escriben los resultados del programa
        self.log = log
        #Monitor para ver la cantidad de paquetes y bytes enviados
        self.monitor = Monitor(serverAddress[0], serverAddress[1], address, archivoElegido)
        #Inicio de un nuevo thread para el cliente con la direccion IP address
        print('Iniciando un nuevo thread para {}'.format(address))
        #Creacion del socket UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Caracteristicas del socket UDP
        self.sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_SNDBUF,
        BUFFER_SIZE)
     
        self.sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_RCVBUF,
        BUFFER_SIZE)
        self.sock.settimeout(0.5)
        self.state = BEG_RECV

    def changeState(self, data):
        self.state = data

    def run(self):
        # Se abre el archivo
        f = open(self.archivoElegido, 'rb')
        #Se lee un chunk de archivo de tamanio BUFFER_SIZE
        data = f.read(BUFFER_SIZE)
        # recv = b''
        cent = False
        while not cent:
            if self.state == RECV:
                cent = True
            else:
                print('Enviando SEND')
                self.sock.sendto(SEND, self.address)
                
        #Se envia un paquete con el nombre del archivo que se va a transferir
        self.sock.sendto(self.archivoElegido[11:].encode(), self.address)
        #Se inicializa un digest que se generara con el mensaje usando el algoritmo MD5
        digest = hashlib.md5()
        #Se captura la fecha en que se inicia la transmision del archivo
        fechaInicioTransmision = datetime.datetime.now()
        self.monitor.start()
        #Mientras aun haya datos por leer y por enviar
        while data:
            #Si se pueden enviar aun datos al cliente, se actualiza el digest y se aniade un paquete
            if(self.sock.sendto(data,self.address)):
                self.monitor.addPacket(len(data))
                digest.update(data)
            data = f.read(BUFFER_SIZE)
        #Una vez se ha culminado el envio de la informacion, se envia el mensaje END_TRANSMISSION
        self.sock.sendto(END_TRANSMISSION, self.address)
        # Se recibe la fecha en que el cliente recibio el ultimo paquete del archivo
        fecha_fin, _ = self.sock.recvfrom(BUFFER_SIZE)
        paq_recibidos, _ = self.sock.recvfrom(BUFFER_SIZE)
        bytes_recibidos, _ = self.sock.recvfrom(BUFFER_SIZE)
        duracionTransmision = datetime.datetime.strptime(fecha_fin.decode(), '%Y-%m-%d %H:%M:%S.%f') - fechaInicioTransmision
        paq_recibidos, bytes_recibidos = paq_recibidos.decode(), bytes_recibidos.decode()
        print("La duracion total de la transmision fue de: %f s" %(duracionTransmision.total_seconds())) 

        #Se envia el digest generado del mensaje/archivo
        print('Se ha enviado el digest')
        digestE = digest.hexdigest().encode()
        self.sock.sendto(digestE, self.address)

        #El servidor recibe del cliente si, al realizar la comprobacion del hash, el archivo fue recibido tal cual se transmition
        entregaExitosa, _ = self.sock.recvfrom(BUFFER_SIZE)
        if entregaExitosa == OK:
            self.monitor.finish(True)
        else:
            self.monitor.finish(False)
        print('Comando recibido: ', repr(entregaExitosa))

        #Se obtiene el reporte de estadisticas generado por el monitor
        stats = self.monitor.getReport()
        print(stats)
        #Se escribe en el log un mensaje de la forma IP_Cliente:Puerto;Mensaje_Recibido_Correcto?OK:ERR;DURACION_TRANSMISION;NUM_PAQUETES_ENVIADOS;NUM_BYTES_ENVIADOS;NUM_PAQUETES_RECIBIDOS;NUM_BYTES_RECIBIDOS;
        self.log.write(self.address[0] + ':' + str(self.address[1]) + ';' + repr(entregaExitosa)[2:-1] + ';' + str(duracionTransmision.total_seconds()) + ';' 
        + str(stats['Packets_sent']) + ';' + str(stats['Bytes_sent']) + ';' + paq_recibidos + ';' + bytes_recibidos +';\n')
        #Se finaliza la comunicacion con el cliente
        print('Finalizando exitosamente la comunicacion con: ' + self.address[0] + ':' + str(self.address[1]))
        #Se envia el comando de finalizacion de envio del archivo
        print('Enviando comando: ', repr(FIN))
        self.sock.sendto(FIN, self.address)
        #Se cierra el socket
        self.sock.close()
