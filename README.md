# sensorika-robot
Lightweight python middleware library for data exchange between mechatronics components.
Sitable for mobile robotics and remote control.

## Requirements
python3, pyzmq, plyvel(leveldb)

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
Serving at 45181
```

3) Read data from it!
```
from sensorika import Connector

c = Connector("127.0.0.1", 45181, 'wifi')
print(c.get())
```
