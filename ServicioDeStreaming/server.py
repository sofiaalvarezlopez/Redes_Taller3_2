import socket as s
import numpy as np
import time
import struct
import cv2

print('Welcome to Streaming Server!')
print('Starting...')

SOCK = s.socket(s.AF_INET, s.SOCK_DGRAM)
BUFFER = 1024
TTL = 1

multicast_ip = '224.1.1.1'
port = 7000

path = 'channels/music/1.mp4'

v = cv2.VideoCapture(path)
frames = []

print('Loading video...')

while v.isOpened():
    ret, f = v.read()
    if ret:
        #fl = []
        #f = cv2.resize(f, (320, 180))
        # f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        #for i in range(f.shape[2]):
            # print(f[:,:,i].shape)
        #    fl.append(f[:,:,i])
        frames.append(f)
    else:
        break

print('Video loaded')

#SOCK.bind((multicast_ip, port))
SOCK.setsockopt(s.IPPROTO_IP, s.IP_MULTICAST_TTL, TTL)

print('Streaming...')

while True:
    n = 0
    for f in frames:
        time.sleep(0.005)
        SOCK.sendto(struct.pack('iii', n, f.shape[0], f.shape[1]), (multicast_ip,port))
        r = 1
        for row in f:
            SOCK.sendto(struct.pack('i', r) + row.tobytes(), (multicast_ip,port))
            r += 1
        n += 1