import logging
import signal
import threading
import time

import zmq

from .connector import Connector
from .tools import getLocalIp

PORT = 15701


class Planner(threading.Thread):
    def __init__(self, programs, *a, **k):
        threading.Thread.__init__(self, args=a, kwargs=k)
        self.programs = programs

class Locator(threading.Thread):
    def __init__(self,*a,**k):
        threading.Thread.__init__(self, args=a, kwargs=k)
        self.programs = dict()
        self.EStop = threading.Event()


    def stop(self,*p1, **p2):
        self.EStop.set()

    def run(self):

        logging.debug("Starting nameserver on {0}:{1}".format(getLocalIp(), str(PORT)))
        time.sleep(1)
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        # socket.bind("tcp://" + config.local_ip + ":" + str(config.name_port))
        try:
            socket.bind("tcp://*:" + str(PORT))
        except:
            self.EStop.set()
            logging.error("port busy")
        programs = {}
        counter = 0

        while not self.EStop.is_set():
            data = {}
            logging.debug('tick')
            # try:
            data = socket.recv_json()
            # except Exception as e:
            #    time.sleep(0.01)
            #    print(e)
            #    continue
            logging.debug('Recive')
            print(data)
            try:
                data['action']
            except:
                data['action'] = 'ping'
            try:
                if data['action'] == 'register':
                    try:
                        data['location']
                    except:
                        data['location'] = 'local'
                    if data['name'] in programs.keys():
                        if programs[data['name']]['port'] != data['port']:
                            print("Reconneting")
                            programs[data['name']]['con'].stop()
                            programs[data['name']]['con'] = Connector(data['ip'], data['port'])
                    else:
                        programs[data['name']] = dict(time=time.time(), ip=data['ip'], port=data['port'],
                                                      location=data['location'])
                        logging.debug("registrating {0} {1}".format(data['name'], data['port']))
                        programs[data['name']]['con'] = Connector(data['ip'], data['port'])
                    socket.send_json(dict(status='ok'))
                    continue
                if data['action'] == 'list':
                    d = []
                    for k, v in programs.iteritems():
                        d.append(dict(name=k, data=v))
                    socket.send_json(d)
                    print('send at', time.time())
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

    def serve(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        print('Serving at {0}'.format(PORT))
        self.start()

def serve():
    l=Locator()
    signal.signal(signal.SIGINT, l.stop)
    signal.signal(signal.SIGTERM, l.stop)
    print('Serving at {0}'.format(PORT))
    l.start()