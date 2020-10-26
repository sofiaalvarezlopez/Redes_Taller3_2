import socket as s
import numpy as np
from queue import Queue
import threading
import struct

class Frame:
    def __init__(self, heigth, width, num):
        self.frame = np.zeros((width, heigth, 3), dtype='uint8')
        self.width = width
        self.heigth = heigth
        self.num = num

    def add_row(self, data):
        row = struct.unpack('i', data[:4])[0]
        row_data = data[4:]
        nprow = np.frombuffer(row_data, dtype='uint8').reshape((1, self.width,3))
        if row == 1:
            self.frame = nprow
        else:
            self.frame = np.append(self.frame, nprow, axis=0)
            # while len(self.frame) <= row:
            #     if len(self.frame) == row:
            #         self.frame = np.append(self.frame, nprow, axis=0)
            #     else:
            #         self.frame = np.append(self.frame, np.zeros((1, self.width, 3)), axis=0)

class BufferCanal:
    def __init__(self, sock):
        self.buffer = Queue()
        self.sock = sock
        self.cent = True
    
    def receiveVideo(self):
        n = 0
        w = 0
        h = 2
        p = 3
        f = []
        rows = []
        p1 = []
        while self.cent:
            msg = self.sock.recvfrom(h*p*8+16)
            if len(msg[0]) == 12:
                num, w, h = struct.unpack('iii', msg[0])
                if len(f) > 0:
                    # self.buffer.put(np.array(f))
                    self.buffer.put(p1)
                #frame = Frame(h,w, num)
                p1 = np.full((w,h,p), 255,dtype="uint8")
                f = []
                rows = []
            elif w>0:
                #frame.add_row(msg[0])
                row = struct.unpack('i', msg[0][:4])[0] -1
                data=np.frombuffer(msg[0][4:],dtype='uint8')
                if len(data)==h*p:
                    framerow = data.reshape(h,p)
                    f.append(framerow)
                    if row not in rows:
                        p1[row,:,:]=framerow
                        rows.append(row)
                #t = threading.Thread(target = frame.add_row,kwargs={'data':msg[0]})
                #t.start()