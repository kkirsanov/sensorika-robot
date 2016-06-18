import threading
import time
import logging
import zmq
import signal
from .tools import getLocalIp

PORT = 15701


class Locator(threading.Thread):
    def stop(self,*p1, **p2):
        #print(p1,p2)
        self.canGo = False

    def run(self):
        self.isStopped = False

        logging.debug("Starting nameserver on {0}:{1}".format(getLocalIp(), str(PORT)))
        time.sleep(1)
        self.canGo = True
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        # socket.bind("tcp://" + config.local_ip + ":" + str(config.name_port))
        try:
            socket.bind("tcp://*:" + str(PORT))
        except:
            self.canGo = False
            logging.error("port busy")
        programs = {}
        counter = 0

        while self.canGo:
            data = {}
            logging.debug('tick')
            try:
                data = socket.recv_json(zmq.DONTWAIT)
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
                    try:
                        data['location']
                    except:
                        data['location'] = 'local'
                    programs[data['name']] = dict(time=time.time(), ip=data['ip'], port=data['port'],
                                                  location=data['location'])
                    logging.debug("registrating {0} {1}".format(data['name'], programs[data['name']]))
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
        self.isStopped = True

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