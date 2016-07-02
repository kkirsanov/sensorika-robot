import json
import time

import zmq

from sensorika import locator
from sensorika.tools import list

ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
socket.connect("tcp://192.168.6.111:{0}".format(locator.PORT))
DATA = dict()
for device in list('192.168.6.111'):
    t = time.time()
    socket.send_json(dict(action='getdata', limit=5000, name=device['name']))
    DATA[device['name']] = socket.recv_json()
    print(time.time() - t, device['name'])

f = open('database2.json', "w")
f.write(json.dumps(DATA))
f.close()

socket.send_json(dict(action='getsessions', limit=3000, ))
DATA = socket.recv_json()

f = open('sessions.json', "w")
f.write(json.dumps(DATA))
f.close()
