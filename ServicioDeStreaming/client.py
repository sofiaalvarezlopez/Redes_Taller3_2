import socket as s
import numpy as np
import cv2
import struct
import time
import threading
from receiver import BufferCanal
from queue import Queue
from tkinter import *
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog

print('Welcome to Streaming Client')
print('Loading settings')

SOCK = s.socket(s.AF_INET, s.SOCK_DGRAM)
BUFFER = 1024

multicast_ip = '224.1.1.1'
port = 7000

SOCK.bind(('',port))

grupo = s.inet_aton(multicast_ip)
SOCK.setsockopt(s.IPPROTO_IP, s.IP_ADD_MEMBERSHIP, struct.pack('4sL', grupo, s.INADDR_ANY))
print("Iniciando captura en la IP: "+multicast_ip+" y puerto: "+str(port))

print('Listening...')

# Variables varias
m=None # Arreglo con  tamaños
Alto=2 # Alto del frame
Capas=2 # Capas de color del Frame
n=[] # Contador
Ancho=0 # Ancho del frame
p=[] #Lista de
p1=[]
n=-1
m = -1
img = np.array([[1,1],[1,1]])

buff = Queue()

buffer = BufferCanal(SOCK)
receive_thread = threading.Thread(target=buffer.receiveVideo)
receive_thread.start()

print('Displaying...')

flag = True

def stop():
    global flag
    flag = not flag
    buffer.buffer = Queue()

root = Tk()
panelA = None
panelB = None
panelA = Label()
panelA.pack(padx=10, pady=10)
btn = Button(root, text="Stop", command=stop)
btn.pack(side="bottom", fill="both", padx="10", pady="10")


# while True:
#     #print('Hola1', len(buff))
#     key = cv2.waitKey(1)
#     if key & 0xFF == ord('q'):
#         break
#     if key & 0xFF == ord(' '):
#         flag = not flag
#     if buffer.buffer.qsize() > 0:
#         #print('hola, ', img.shape)
#         if flag:
#             img = buffer.buffer.get()
#             image = Image.fromarray(img)
#             image = ImageTk.PhotoImage(image)
#             panelA.configure(image=image)
#             panelA.image = image
#             cv2.imshow('Test', img)
#         else:
#             buffer.buffer = Queue()

def task():
    if buffer.buffer.qsize() > 0:
        #print('hola, ', img.shape)
        if flag:
            img = buffer.buffer.get()
            image = Image.fromarray(img)
            #image = ImageTk.PhotoImage(image)
            panelA.configure(image=image)
            panelA.image = image
    root.after(10, task)
root.after(10, task)
root.mainloop()

buffer.cent = False
cv2.destroyAllWindows()
cv2.waitKey(1)


# btn = Button(root, text="Select an image", command=select_image)
# btn.pack(side="bottom", fill="both", expand="yes", padx="10", pady="10")
# kick off the GUI