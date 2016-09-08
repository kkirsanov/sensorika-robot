import datetime
import threading
import time

import zmq


class Connector:
    def __init__(self, ip, port=15701, name=""):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.addr = "tcp://" + ip + ":" + str(port)
        self.socket.connect(self.addr)
        self.t0 = time.time() - 10000
        self.dataReady = False
        t = str(datetime.datetime.now())
        self.cache = None

        self.Estop = threading.Event()

    def get(self, count=1, dt=0.05):
        if (self.t0 + dt > time.time()) and (self.dataReady):
            return self.cache
        else:
            self.socket.send_json(dict(action='get', count=count))
            self.cache = self.socket.recv_json()
            self.t0 = time.time()
            self.dataReady = True
            return self.cache

    def set(self, data=None):
        data = dict(action='set', data=data, count=1)
        self.socket.send_json(data)
        return self.socket.recv_json()

    def stop(self):
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
