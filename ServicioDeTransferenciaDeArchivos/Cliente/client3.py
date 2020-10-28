import socket
import sys
import datetime
import hashlib
from hmac import compare_digest
import os
from udp_monitor2 import Monitor

#Se crea un socket para manejar la comunicacion cliente-servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.2)
#IP de la instancia/MV/maquina donde se corre el servidor. para correr de manera local, usar localhost
serverAddress = ('54.226.145.99', 10000)
serverAddress = ('localhost', 10000)
serverAddress = ('ec2-54-226-145-99.compute-1.amazonaws.com', 10000)
#Comando que indica que el cliente esta listo para recibir archivos
BEG_RECV = b'BEG_RECV'
SEND = b'SEND'
RECV = b'RECV'
#Comando que indica que el archivo se recibio correctamente 
OK = b'OK'
#Comando que indica que hubo un error en la comunicacion o que el archivo no se recibio adecuadamente
ERR = b'ERR'
#Comando que indica la finalizacion de la transmision del archivo enviado
END_TRANSMISSION = b'END_TRANSMISSION'
#Comando que indica la finalizacion del protocolo
FIN = b'FIN'
#Se define el tamanio del buffer
buffer = 1024
#Se crea un monitor
monitor = Monitor(serverAddress[0], serverAddress[1], '', '')

try:
    tcpsock.connect(serverAddress)
    #Se envia el mensaje de que se esta listo para recibir archivos
    print('El cliente esta listo para recibir archivos: {}'.format(BEG_RECV))
    sent = sock.sendto(BEG_RECV, serverAddress)
    data, address = sock.recvfrom(buffer)
    print('Esperando SEND')
    cent = False
    while not cent:
        try:
            print('Esperando SEND')
            data, address = sock.recvfrom(buffer)
            print(data)
            if data == SEND:
                cent = True
                print('REcibido SEND')
            else:
                print('Reenviando BEG_RECV')
                sent = sock.sendto(BEG_RECV, serverAddress)
        except:
            pass
    cent = False
    print(SEND, 'recibido')
    data = SEND
    while not cent:
        try:
            print('Esperando nomre')
            data, address = sock.recvfrom(buffer)
            if data != SEND:
                cent = True
            else:
                sent = sock.sendto(RECV, serverAddress)
                print('Reenviando RECV')
        except:
            pass
    #Se obtiene el nombre del archivo que se debe enviar
    print ("Archivo a recibir:",data.strip())
    #Se crea el archivo donde se almacenaran los datos
    f = open('./Cliente/' + repr(data.strip())[2:-1], "wb")
    #Se genera un digest
    digestGenerado = hashlib.md5()
    #Se recibe un chunk de datos de tamanio buffer.
    data, address = sock.recvfrom(buffer)
    #Mientras aun haya datos por leer, se escribe en el archivo, se actualiza el digest
    #Se para cuando se reciba el comando END_TRANSMISSION 
    while data:
        #Se escribe en el archivo los datos que se acaban de leer
        f.write(data)
        #Se actualiza el digest con los datos leidos
        digestGenerado.update(data)
        monitor.addPacket(len(data))
        data,addr = sock.recvfrom(buffer)
        #Si se recibe el final de la transmision, se captura la fecha, se envia al servidor y se cierra el archivo
        if (data == END_TRANSMISSION):
            stats = monitor.getReport()
            print(stats)
            fechaFinTransmision, paquetes_recibidos, bytes_recibidos = str(datetime.datetime.now()), str(stats['Packets_sent']), str(stats['Bytes_sent'])
            sock.sendto(fechaFinTransmision.encode(), addr)
            sock.sendto(paquetes_recibidos.encode(), addr)
            sock.sendto(bytes_recibidos.encode(), addr)
            print('Fecha fin transmision archivo: ', fechaFinTransmision)
            f.close()
            print('Comando recibido: ', repr(END_TRANSMISSION))
            break
    digestG = digestGenerado.hexdigest().encode()
    print(digestG)
    #Se recibe el digest del servidor
    digestRecibido, addr = sock.recvfrom(buffer)
    print(digestRecibido)
    #Si el digest generado y el digest recibido no coinciden, se envia un mensaje de error.
    #Se finaliza la comunicacion con el servidor.
    if not compare_digest(digestG, digestRecibido):
        sock.sendto(ERR, addr)
        print('Comando enviado: ', repr(ERR))
        print('La integridad del archivo no pudo ser verificada. Finalizando conexion.')
        sock.close()
        exit()

    sock.sendto(OK, addr)

    print('La integridad del archivo pudo ser verificada correctamente.')
    print('Comando enviado: ', repr(OK))


    fin, _ = sock.recvfrom(buffer)
    if(repr(fin) != repr(FIN)):
        print('La tarea ha fallado exitosamente')    
        sock.close()
        exit()
    print('Comando recibido: ' + repr(FIN))
    print('Protocolo finalizado exitosamente. Gracias por conectarse al servidor.')
    exit()
    
finally:
    sock.close()
    tcpsock.close()