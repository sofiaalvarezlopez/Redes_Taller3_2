import socket
from threading import Thread
from socketserver import ThreadingMixIn
import struct
import datetime
import os
import hashlib
import sys
from udp_monitor2 import Monitor

BUFFER_SIZE = 1024
serverAddress = ('localhost', 10000)
BEG_RECV = b'BEG_RECV'
OK = b'OK'
ERR = b'ERR'
END_TRANSMISSION = b'END_TRANSMISSION'
FIN = b'FIN'

class ClientHandler(Thread):
    def __init__(self, address, sock, archivoElegido, log):
        Thread.__init__(self)
        self.address = address
        self.sock = sock
        self.archivoElegido = archivoElegido
        self.log = log
        self.monitor = Monitor(serverAddress[0], serverAddress[1], address, archivoElegido)
        #self.scanner = scanner
        print('Iniciando un nuevo thread para {}'.format(address))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_SNDBUF,
        BUFFER_SIZE)
     
        self.s.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_RCVBUF,
        BUFFER_SIZE)

    def run(self):
        f = open(self.archivoElegido, 'rb')
        data = f.read(BUFFER_SIZE)
        self.s.sendto(self.archivoElegido[11:].encode(), self.address)
        digest = hashlib.md5()
        fechaInicioTransmision = datetime.datetime.now()
        self.monitor.start()
        while data:
            if(self.s.sendto(data,self.address)):
                self.monitor.addPacket(len(data))
                digest.update(data)
            data = f.read(BUFFER_SIZE)
        self.s.sendto(END_TRANSMISSION, self.address)
        fechaFinTransmision, _ = self.s.recvfrom(BUFFER_SIZE)
        duracionTransmision = datetime.datetime.strptime(fechaFinTransmision.decode(), '%Y-%m-%d %H:%M:%S.%f') - fechaInicioTransmision
        print("La duracion total de la transmision fue de: %f s" %(duracionTransmision.total_seconds())) 

        print('se ha enviado el digest')
        digestE = digest.hexdigest().encode()
        self.s.sendto(digestE, self.address)

        entregaExitosa, _ = self.s.recvfrom(BUFFER_SIZE)
        if entregaExitosa == OK:
            self.monitor.finish(True)
        else:
            self.monitor.finish(False)
        print('Comando recibido: ', repr(entregaExitosa))

        #print('Numero de bytes enviados: ', stats['bytes_sent'])
        #print('El cliente ' + self.ip + ':' + str(self.port) + ' recibio ' + str(stats['bytes_received']) + ' bytes')
        stats = self.monitor.getReport()
        print(stats)
        self.log.write(stats)
        self.log.write(self.address[0] + ':' + str(self.address[1]) + ';' + repr(entregaExitosa)[2:-1] + ';' + str(duracionTransmision.total_seconds()) + ';\n')
        
        print('Finalizando exitosamente la comunicacion con: ' + self.address[0] + ':' + str(self.address[1]))
        print('Enviando comando: ', repr(FIN))
        self.s.sendto(FIN, self.address)
        self.s.close()