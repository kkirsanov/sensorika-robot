from sensorika import Connector
import time

c = Connector("127.0.0.1", 35741, 'wifi')
for x in range(10):
    print(c.get())
    time.sleep(1)