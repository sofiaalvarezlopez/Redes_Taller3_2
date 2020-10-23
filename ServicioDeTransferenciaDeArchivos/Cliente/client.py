import socket
import sys
import datetime
import hashlib
from hmac import compare_digest
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverAddress = ('localhost', 10000)
BEG_RECV = b'BEG_RECV'
OK = b'OK'
ERR = b'ERR'
END_TRANSMISSION = b'END_TRANSMISSION'
FIN = b'FIN'
buffer = 1024

try:
    print('enviado datos {}'.format(BEG_RECV))
    sent = sock.sendto(BEG_RECV, serverAddress)

    data, address = sock.recvfrom(buffer)
    print ("Received File:",data.strip())
    f = open('./Cliente/' + repr(data.strip())[2:-1],"wb")

    digestGenerado = hashlib.md5()

    digestGenerado.update(data)
    data, address = sock.recvfrom(buffer)
    while data:
        f.write(data)
        digestGenerado.update(data)
        print(data)
        data,addr = sock.recvfrom(buffer)
        if (data == END_TRANSMISSION):
            print('esta aca')
            fechaFinTransmision = str(datetime.datetime.now())
            sock.sendto(fechaFinTransmision.encode(), addr)
            print('Fecha fin transmision archivo: ', fechaFinTransmision)
            f.close()
            print('Comando recibido: ', repr(END_TRANSMISSION))
            break

    digestG = digestGenerado.hexdigest().encode()
    print(digestG)
    digestRecibido, _ = sock.recvfrom(buffer)
    print(digestRecibido)
    if not compare_digest(digestG, digestRecibido):
        sock.sendto(ERR, serverAddress)
        #os.remove(archivoElegido)
        print('Comando enviado: ', repr(ERR))
        print('La integridad del archivo no pudo ser verificada. Finalizando conexion.')
        sock.close()
        exit()

    sock.sendto(OK, serverAddress)

    print('La integridad del archivo pudo ser verificada correctamente.')
    print('Comando enviado: ', repr(OK))


    fin, _ = sock.recvfrom(buffer)
    if(repr(fin) != repr(FIN)):
        print('La tarea ha fallado exitosamente')    
        s.close()
        exit()
    print('Comando recibido: ' + repr(FIN))
    print('Protocolo finalizado exitosamente. Gracias por conectarse al servidor.')
    s.close()
    exit()
    
finally:
    sock.close()