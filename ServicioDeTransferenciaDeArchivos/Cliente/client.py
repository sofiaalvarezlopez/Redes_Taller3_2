import socket
import sys
import datetime

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

    data, address = sock.recvfrom(buffer)
    while data:
        f.write(data)
        data,addr = sock.recvfrom(buffer)
        if (data == END_TRANSMISSION):
            print('esta aca')
            fechaFinTransmision = str(datetime.datetime.now())
            sock.sendto(fechaFinTransmision.encode(), address)
            print('Fecha fin transmision archivo: ', fechaFinTransmision)
            f.close()
            print('Comando recibido: ', repr(END_TRANSMISSION))
            break
    
    
finally:
    sock.close()