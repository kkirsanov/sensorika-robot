import json
import logging
import signal
import threading
import time

import plyvel
import zmq

from .connector import Connector
from .tools import getLocalIp

PORT = 15701


class Planner(threading.Thread):
    def __init__(self, programs, *a, **k):
        threading.Thread.__init__(self, args=a, kwargs=k)
        self.programs = programs


class ThreadedConnector(threading.Thread):
    def __init__(self, ip, port, params=None, database=None, *args, **kwargs):
        threading.Thread.__init__(self, args=args, kwargs=args)
        try:
            if params:
                self.params = params
            else:
                import random
                self.params = dict(frequency=1.0, name='none_{0}'.format(random.randint(0, 1000)))
            self.Estop = threading.Event()
            self.connector = Connector(ip, port)
            self.data = []

            self.db = database
            self.name = self.params['name']
            self.db.statSession(self.name)
            self.thread = self.start()
        except Exception as e:
            print(e)

    def run(self):
        while not self.Estop.is_set():
            time.sleep(1 / self.params['frequency'])

            data = self.connector.get()
            t, d = data
            # do not store equal data
            canAdd = False
            if self.data:
                if self.data[-1][0] != t:
                    canAdd = True
            else:
                canAdd = True
            if canAdd:
                if isinstance(t, float):
                    self.data.append(([time.time()] + [t], d))
                else:
                    self.data.append(([time.time()] + t, d))
                self.db.add(self.name, self.data[-1])
            if len(self.data) > 100:
                self.data = self.data[-100:]

    def stop(self):
        self.Estop.set()


class DatabaserLEVELDB():
    def __init__(self):
        self.db = plyvel.DB('./db', create_if_missing=True)

    def close(self):
        if not self.db.closed:
            self.db.close()
    def statSession(self, name):
        self.db.put("session|{1}|{0}".format(name, time.time()).encode('utf8'), b'ok')

    def add(self, name, data):
        if not self.db.closed:
            self.db.put("{0}-{1}".format(name, time.time()).encode('utf8'), json.dumps(data).encode("utf8"))

    def getSessions(self):
        d = []
        for k, v in self.db.iterator(start=b'session', stop=b'session.'):
            d.append(k)
        return d


class Locator(threading.Thread):
    def __init__(self, *a, **k):
        threading.Thread.__init__(self, args=a, kwargs=k)
        self.programs = dict()
        self.EStop = threading.Event()
        self.db = DatabaserLEVELDB()

    def stop(self, *p1, **p2):
        for k, v in self.programs.items():
            v['con'].stop()
            self.EStop.set()
        self.db.close()
        print("STOP!")

    def run(self):

        logging.debug("Starting nameserver on {0}:{1}".format(getLocalIp(), str(PORT)))
        time.sleep(1)
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        try:
            socket.bind("tcp://*:" + str(PORT))
        except:
            self.EStop.set()
            logging.error("port busy")
        self.programs = {}
        counter = 0

        while not self.EStop.is_set():
            data = {}
            logging.debug('tick')
            try:
                data = socket.recv_json(zmq.DONTWAIT)
                print(data)
            except Exception as e:
                time.sleep(0.01)
                continue
            logging.debug('Recive')
            try:
                data['action']
            except:
                data['action'] = 'ping'
            try:
                if data['action'] == 'register':
                    print("registarting")
                    try:
                        data['location']
                    except:
                        data['location'] = 'local'
                    if data['name'] in self.programs.keys():
                        if self.programs[data['name']]['port'] != data['port']:
                            self.programs[data['name']]['params'] = data['params']
                            self.programs[data['name']]['con'].stop()
                            self.programs[data['name']]['con'] = ThreadedConnector(data['ip'], data['port'],
                                                                                   database=self.db,
                                                                                   params=data['params'])
                    else:
                        self.programs[data['name']] = dict(time=time.time(), params=data['params'])
                        self.programs[data['name']]['con'] = ThreadedConnector(data['ip'], data['port'],
                                                                               database=self.db, params=data['params'])
                    socket.send_json(dict(status='ok'))
                    continue
                if data['action'] == 'list':
                    d = []
                    for k, v in self.programs.items():
                        d.append(dict(name=k, data=v['params']))  # TODO: Fix, couse` ThreadedConnector is not json
                    socket.send_json(d)
                    continue
                if data['action'] == 'listsessions':
                    socket.send_json(self.db.getSessions())
                    continue
                if data['action'] == 'get':
                    if 'count' not in data.keys():
                        data['count'] = 1
                    if 'name' not in data.keys():
                        # get all data
                        tmp = dict()
                        for k, v in self.programs.items():
                            tmp[k] = v['con'].data[-data['count']:]
                        print(tmp, self.programs)
                        socket.send_json(dict(status='ok', data=tmp))
                        continue
                    else:
                        d = self.programs[data['name']]['con'].data[-data['count']:]
                        socket.send_json(dict(status='ok', data=d))
                        continue

                if data['action'] == 'ping':
                    socket.send_json(dict(status='ok'))
                    continue
            except Exception as e:
                socket.send_json(dict(status='fail', text=str(e)))
                continue

            socket.send_json(dict(status='fail', text='wrong action'))

        socket.close()
        context.term()

        time.sleep(0.01)
        logging.debug("closing")


def serve():
    l = Locator()
    signal.signal(signal.SIGINT, l.stop)
    signal.signal(signal.SIGTERM, l.stop)
    print('Serving at {0}'.format(PORT))
    l.start()
