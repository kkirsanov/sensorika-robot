import json, zmq
import  logging
import time

PORT = 15701
def getLocalIp():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.153', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def tryConnect(ip=getLocalIp(), port=PORT, timeout=4, dt=0.01):
    ok = None
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + str(ip) + ":" + str(port))
    socket.send_json({"action": "list"})
    # print "send at ", time.time()
    t = time.time()
    while t + timeout > time.time():
        try:
            socket.recv_json(zmq.DONTWAIT)
            ok = (ip, port)
        except Exception as e:
            time.sleep(dt)
            continue
    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()
    return ok

def list(ns_ip=getLocalIp(), name=""):
    lcontext = zmq.Context()
    lsocket = lcontext.socket(zmq.REQ)
    lsocket.connect("tcp://" + ns_ip + ":" + str(PORT))
    lsocket.send_json(dict(action='list'))
    d = lsocket.recv_json(); lsocket.close()
    ret = []
    if name:
        for x in d:
            if x['name'].lower() == name.lower():
                ret.append(x)
        return ret
    else:
        return d
