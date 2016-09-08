from sensorika import Worker
import time
import subprocess
import threading

def getWifi():
    """
    dsasdfdsfdsfds
    :return:
    """
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



import signal
st=threading.Event()
def doStop(*args, **kwargs):
    st.set()

signal.signal(signal.SIGINT, doStop)
signal.signal(signal.SIGTERM, doStop)

w=Worker('wifi')
while not st.is_set():
    result = getWifi()
    w.add(result)
    time.sleep(1)
    print(result)

w.stop()
