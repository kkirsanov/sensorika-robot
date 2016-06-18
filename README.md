# sensorika-robot
Lightweight python middleware libriry for mechatronics components

## requirements
python3, pyzmq

## Excample Usage
1) Create simpe sensor application:
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

2) Remotely read data from it!
```
from sensorika import Connector

c = Connector("127.0.0.1", 35741, 'wifi')
print(c.get())
```