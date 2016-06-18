import zmq, time, datetime

class Connector:
    def __init__(self, ip, port, name=""):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.addr = "tcp://" + ip + ":" + str(port)
        self.socket.connect(self.addr)
        self.t0 = time.time() - 10000
        self.dataReady = False
        t = str(datetime.datetime.now())
        #self.file = open("log_{name}_{ip}_{port}_{time}".format(name=name, ip=ip, port=port, time=t), "w")

    def get(self, dt=0.05):
        if (self.t0 + dt > time.time()) and (self.dataReady):
            return self.cache
        else:
            # print 'call'
            #self.file.write("> {0} 1\n".format(time.time()))
            self.socket.send_json(dict(action='get', count=1))
            self.cache = self.socket.recv_json()
            #self.file.write("< {0} {1}\n".format(time.time(), self.cache))
            self.t0 = time.time()
            self.dataReady = True
            return self.cache

    def set(self, data=None):
        data = dict(action='set', data=data, count=1)
        #self.file.write("> {0} {1}\n".format(time.time(), json.dumps(data)))
        self.socket.send_json(data)
        return self.socket.recv_json()

    def stop(self):
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
        # self.socket.disconnect(self.addr)