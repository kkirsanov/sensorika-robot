import zmq

ctx = zmq.Context()
s = ctx.socket(zmq.REQ)
ip = '127.0.0.1'
port = 15701
s.connect("tcp://" + ip + ":" + str(port))

s.send_json(dict(action='list'))
d = s.recv_json()
print(d)

s.send_json(dict(action='get', count=2, name='wifi'))
d = s.recv_json()
print(d)
