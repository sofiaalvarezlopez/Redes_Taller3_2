import os, socket as s, time, struct, json, cv2

PATH = os.path.realpath(__file__)
PATH = os.path.dirname(PATH)

TTL = 1

class Channel:
    def __init__(self, id, host):
        self.id = id
        self.host = host
        self.path = os.path.join(PATH, 'channels', id)
        self.stream = True
        self.frames = []
        self.load_info()

    def load_info(self):
        with open(os.path.join(self.path, 'info.txt'), 'r') as infof:
            info = json.loads(infof.read())
            self.name = info['name']
            self.desc = info['description']
            self.videos = info['videos']

    def load_videos(self):
        for vname in self.videos:
            vpath = os.path.join(self.path, vname)
            v = cv2.VideoCapture(vpath)
            while v.isOpened():
                ret, f = v.read()
                if ret:
                    self.frames.append(f)
                else:
                    break

    def start_streaming(self):
        if len(self.frames) == 0:
            raise Exception('Load video first')
        self.stream = True
        with s.socket(s.AF_INET, s.SOCK_DGRAM) as SOCK:
            SOCK.setsockopt(s.IPPROTO_IP, s.IP_MULTICAST_TTL, TTL)

            while self.stream:
                n = 0
                for f in self.frames:
                    time.sleep(0.005)
                    SOCK.sendto(struct.pack('iii', n, f.shape[0], f.shape[1]), self.host)
                    r = 1
                    if not self.stream:
                        break
                    for row in f:
                        SOCK.sendto(struct.pack('i', r) + row.tobytes(), self.host)
                        r += 1
                n += 1

    def stop_streaming(self):
        self.stream = False

    def printPath(self):
        print(self.path)