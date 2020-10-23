import socket
from threading import Thread
from socketserver import ThreadingMixIn
import struct
import datetime
import os
import hashlib
import sys

BUFFER_SIZE = 1024
serverAddress = ('localhost', 10000)
BEG_RECV = b'BEG_RECV'
OK = b'OK'
ERR = b'ERR'
END_TRANSMISSION = b'END_TRANSMISSION'
FIN = b'FIN'

class ClientHandler(Thread):
    def __init__(self, address, sock, archivoElegido):
        Thread.__init__(self)
        self.address = address
        self.sock = sock
        self.archivoElegido = archivoElegido
        #self.log = log
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
        self.s.sendto(data, self.address)
        fechaInicioTransmision = datetime.datetime.now()
        while data:
            if(self.s.sendto(data,self.address)):
                print ("sending ...")
            data = f.read(BUFFER_SIZE)
        self.s.sendto(END_TRANSMISSION, self.address)
        fechaFinTransmision, address = self.s.recvfrom(BUFFER_SIZE)
        duracionTransmision = datetime.datetime.strptime(fechaFinTransmision.decode(), '%Y-%m-%d %H:%M:%S.%f') - fechaInicioTransmision
        print("La duracion total de la transmision fue de: %f s" %(duracionTransmision.total_seconds())) 
        