import socket as s, struct, os, json
from channel import Channel
from threading import Thread

CHANNELS_PATH = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'channels')
CHANNELS_INFO_FILE = 'channels.txt'

print('Welcome to Streaming Server!')
print('Starting...')

SOCK = s.socket(s.AF_INET, s.SOCK_DGRAM)
TTL = 1

multicast_ip = '224.1.1.1'
start_port = 7000
info_port = 6999

SOCK.setsockopt(s.IPPROTO_IP, s.IP_MULTICAST_TTL, TTL)

STATE = True

channels = []
threads = []

def send_channels_info():
    info = []
    print('Loading channels info')
    for channel in channels:
        cha = {}
        cha['name'] = channel.name
        cha['desc'] = channel.desc
        cha['port'] = channel.host[1]
        info.append(cha)
    infostr = json.dumps(info)
    print('Broadcasting channels info')
    while STATE:
        SOCK.sendto(infostr.encode('utf-8'), (multicast_ip,info_port))

def create_channels():
    print('Searching for channels')
    fcha = os.path.join(CHANNELS_PATH, CHANNELS_INFO_FILE)
    with open(fcha, 'r') as infof:
        name = infof.readline()
        while name:
            if name.startswith('!'):
                name = infof.readline()
                continue
            new_channel = Channel(name.strip(), (multicast_ip, start_port + len(channels) + 1))
            channels.append(new_channel)
            print('Channel', name, 'found. Transmitting on', new_channel.host[1])
            name = infof.readline()
    print('Channels search done')

def send_basic_info():
    print('Broadcasting basic info')
    while STATE:
        SOCK.sendto(('Channel info on '+str(start_port)).encode('utf-8'), (multicast_ip,start_port))

def start_channels():
    for channel in channels:
        print('Loading channel', channel.name, 'videos')
        channel.load_videos()
        print('Channel', channel.name, 'videos loaded')
        t = Thread(target=channel.start_streaming)
        print('Channel', channel.name, 'streaming')
        t.start()
        threads.append(t)

def stop_channels():
    print('Stopping channels streaming')
    for channel in channels:
        channel.stop_streaming()
        print('Channel', channel.name, 'stopped')
    print('Channels streaming stopped')

print('Streaming...')

create_channels()
start_channels()
t1 = Thread(target=send_basic_info)
t1.start()
t2 = Thread(target=send_channels_info)
t2.start()