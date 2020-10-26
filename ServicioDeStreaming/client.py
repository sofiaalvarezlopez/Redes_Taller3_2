import socket as s, numpy as np, cv2, struct, time, threading, json, inspect
from receiver import BufferCanal
from queue import Queue
from functools import partial
from tkinter import *
from PIL import Image, ImageTk
from tkinter.ttk import Frame, Button, Style

print('Welcome to Streaming Client')
print('Loading settings')

BUFFER = 2**16

multicast_ip = '224.1.1.1'
start_port = 7000
info_port = 6999
actual_port = start_port

START_IMAGE = gauss = np.random.uniform(0, 255,(360,640,3)).astype(np.uint8).reshape((360,640,3))
print(START_IMAGE.shape)

def start_SOCK(port):
    global SOCK
    SOCK = s.socket(s.AF_INET, s.SOCK_DGRAM)
    SOCK.bind(('',port))
    group = s.inet_aton(multicast_ip)
    SOCK.setsockopt(s.IPPROTO_IP, s.IP_ADD_MEMBERSHIP, struct.pack('4sL', group, s.INADDR_ANY))

start_SOCK(start_port)

print('Listening...')

buffer = BufferCanal(SOCK)

channels = []

def load_channels():
    global channels
    with s.socket(s.AF_INET, s.SOCK_DGRAM) as sock:
        sock.bind(('',info_port))
        group = s.inet_aton(multicast_ip)
        sock.setsockopt(s.IPPROTO_IP, s.IP_ADD_MEMBERSHIP, struct.pack('4sL', group, s.INADDR_ANY))
        raw_info = sock.recvfrom(BUFFER)
        if len(raw_info[0]) > 10:
            channels = json.loads(str(raw_info[0], 'utf-8'))

def receive():
    buffer.sock = SOCK
    receive_thread = threading.Thread(target=buffer.receiveVideo)
    receive_thread.start()
    return receive_thread

recThread = receive()

print('Displaying...')

flag = True

def change_channel(port):
    global buffer
    global recThread
    global actual_port
    global panel
    buffer.cent = False
    buffer.buffer = Queue()
    recThread.join()
    buffer.cent = True
    actual_port = port
    SOCK.close()
    start_SOCK(actual_port)
    recThread = receive()
    time.sleep(0.5)
    down = port - 1
    up = port + 1
    isdown = False
    isup = False
    panel['text'] = 'Channel ' + str(port)
    for i in channels:
        if i['port'] == down:
            isdown = True
        elif i['port'] == up:
            isup = True
    if isdown:
        btnDown['state'] = NORMAL
    else:
        btnDown['state'] = DISABLED
    if isup:
        btnUp['state'] = NORMAL
    else:
        btnUp['state'] = DISABLED

def channel_down():
    global actual_port
    change_channel(actual_port-1)

def channel_up():
    global actual_port
    change_channel(actual_port+1)

def stop():
    global flag
    flag = not flag
    buffer.buffer = Queue()
    if flag:
        btnStop.configure(text='Stop')
    else:
        btnStop.configure(text='Play')

def refreshChannels():
    global chanBns
    global channels
    load_channels()
    for i in chanBns:
        i.destroy()
    chanBns = []
    for i in channels:
        port = i['port']
        chanBns.append(Button(panelChan, text=i['name'], command=partial(change_channel, port)))
    for i in chanBns:
        i.pack(padx=10, pady=(10,0))
    change_channel(channels[0]['port'])

root = Tk()
root.title('UDP Television')
style = Style()
style.theme_use('clam')

#Panel creation

panelTitle = Frame(root)
panelContent = Frame(root)

panelTitle.pack(side=TOP)
panelContent.pack(side=BOTTOM)

panelRight = Frame(panelContent)
panelRight.pack(side=RIGHT, fill=BOTH)
panelLeft = Frame(panelContent)
panelLeft.pack(side=LEFT, fill=BOTH)

panelBtn = Frame(panelRight)
panelBtn.pack(side=BOTTOM)

#Title panel widgets

title = Label(panelTitle, text='UDP Television', font=("Arial bold", 30))
title.pack(fill=X, padx=10, pady=10)

#Left panel widgets

channelsLbl = Label(panelLeft, text='Channels')
contentLeft = Frame(panelLeft)

channelsLbl.pack(side=TOP, fill=X, padx=10, pady=10)
contentLeft.pack(fill=BOTH)

#Content left widgets

style.configure('style.TFrame', background='white')
panelChan = Frame(contentLeft, style='style.TFrame')
chanBns = []
refreshBtn = Button(contentLeft, text='Refresh', command=refreshChannels)

panelChan.pack(side=TOP, fill=BOTH, ipady=5)
refreshBtn.pack(side=BOTTOM, padx=10, pady=10)

#Right panel widgets

panel = Label(panelRight, text='Channel', compound=BOTTOM)
panel.pack(fill=BOTH, padx=(0,10))


btnDown = Button(panelBtn, text='Down', command=channel_down, state=DISABLED)
btnStop = Button(panelBtn, text="Stop", command=stop)
btnUp = Button(panelBtn, text='Up', command=channel_up)

btnUp.pack(side=RIGHT, padx="10", pady="10")
btnStop.pack(side=RIGHT, padx="10", pady="10")
btnDown.pack(side=RIGHT, padx="10", pady="10")

def task():
    img = START_IMAGE
    if flag:
        if buffer.buffer.qsize() > 0:
            img = cv2.cvtColor(buffer.buffer.get(), cv2.COLOR_BGR2RGB)
        try:
            image = Image.fromarray(img)
            image = ImageTk.PhotoImage(image)
            panel.configure(image=image)
            panel.image = image
        except Exception as e:
            print(e)

    root.after(80, task)
root.after(80, task)
root.mainloop()

buffer.cent = False
