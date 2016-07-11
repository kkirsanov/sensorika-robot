# sensorika-robot
Lightweight python middleware library for data exchange between mechatronics components in synchronous and asynchronous way.
Sitable for mobile robotics and remote control.

## Requirements
python2/3, pyzmq, plyvel(for leveldb), inputs (for joystic), ujson (for better perfomance)

## Example Usage
1) Create simple sensor application:
```
from sensorika import worker
import subprocess

def getWifi():
    z = subprocess.check_output(['iwconfig']).decode("utf8")
    a = z.split("\n")
    for x in a:
        if 'Quality' in x:
            try:
                a, b = x.split('=')[1].split(' ')[0].split("/")
                return float(a) / float(b)
            except:
                return 0
    return 0

worker.mkPeriodicWorker("wifi", getWifi)
```

3) Run it and watch for output:
```
Serving at sync 41163 and async 37553
```

3) Read data from it!
```
from sensorika import Connector

c = Connector("127.0.0.1", 45181, 'wifi')
print(c.get())
```

or
```
import time
from sensorika import ConnectorAsync

def prn(x):
    print(x)

c = ConnectorAsync("127.0.0.1", 37553, 'wifi', callback=prn)

time.sleep(10)
c.stop()
```
