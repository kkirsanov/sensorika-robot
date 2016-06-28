import subprocess

from sensorika import worker


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


worker.mkPeriodicWorker("wifi", getWifi, dict(frequency=1.0))
