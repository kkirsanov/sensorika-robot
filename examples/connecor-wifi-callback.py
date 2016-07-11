import time

from sensorika import ConnectorAsync


def prn(x):
    print(x)


c = ConnectorAsync("127.0.0.1", 37553, 'wifi', callback=prn)

for x in range(5):
    time.sleep(1)

c.stop()
