import time, datetime

class Monitor:
    def __init__(self, host, port, client, filename):
        self.host = host
        self.port = port
        self.client = client
        self.filename = filename
        self.success = False
        self.len_data = []
        self.done = False

    def start(self):
        self.time = datetime.datetime.now()
        self.start_time = time.time()

    def addPacket(self, len_dat):
        self.len_data.append(len_dat)

    def finish(self, success):
        self.success = success
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time
        self.done = True

    def getReport(self):
        if self.done:
            return {'Success': self.success, 'Packets_sent': len(self.len_data), 'Bytes_sent': sum(self.len_data)}
            #return 'Host: {} Port: {} Client: {} File: {} Success: {} Packets_sent: {} Bytes_sent: {} Duration: {}'.format(self.host, self.port, self.client, self.filename, self.success, len(self.len_data), sum(self.len_data), self.total_time)
        else:
            return 'Monitoring not finished. Host: {} Port: {} Client: {} File: {} Success: {} Packets_sent: {} Bytes_sent: {}'.format(self.host, self.port, self.client, self.filename, self.success, len(self.len_data), sum(self.len_data))
            

    