# control for Cobra M5 joystic
import threading
import time

from examples.sensorika.inputs import get_gamepad


class Joy(threading.Thread):
    def __init__(self, *a, **k):
        self.Estop = threading.Event()
        self.joystat = dict(x=0, y=0, speed=0, grip=False, hobot=False, lx=0, ly=0, dx=0, dy=0, spin=0)
        super(Joy, self).__init__()
        self.thread = self.start()

    def run(self):
        while not self.Estop.is_set():
            events = get_gamepad()
            for event in events:
                # print(self.joystat)
                # if event.code not in ('ABS_Y', 'ABS_X', 'SYN_REPORT'):
                if event.ev_type == 'Absolute':
                    if event.code == 'ABS_HAT0X':
                        self.joystat['dx'] = event.state
                    if event.code == 'ABS_HAT0Y':
                        self.joystat['dy'] = -event.state
                    if event.code == 'ABS_X':
                        self.joystat['x'] = -(512 - event.state) / 512.0
                    if event.code == 'ABS_Y':
                        self.joystat['y'] = (512 - event.state) / 512.0
                    if event.code == 'ABS_THROTTLE':
                        self.joystat['speed'] = event.state / 255.0
                    if event.code == 'ABS_RUDDER':
                        self.joystat['spin'] = event.state - 128

                if event.ev_type == 'Sync':
                    continue
                if event.ev_type == 'Key':
                    if event.code == 'BTN_DEAD':
                        self.joystat['hobot'] = event.state == 1
                        continue
                    if event.code == 'BTN_TRIGGER':
                        self.joystat['grip'] = event.state == 1
                        continue
                    if event.code == 'UNKNOWN_300':
                        self.joystat['ly'] = event.state
                    if event.code == 'UNKNOWN_302':
                        self.joystat['ly'] = -event.state
                    if event.code == 'BTN_BASE6':
                        self.joystat['lx'] = event.state
                    if event.code == 'UNKNOWN_301':
                        self.joystat['lx'] = -event.state

    def stop(self):
        self.Estop.set()


from sensorika import Connector
from sensorika.tools import list as nslist

ns = "192.168.6.111"
l = nslist(ns, "OmniDrive")[0]
drive = Connector(ns, l["data"]["port"])
l = nslist(ns, "Hobot")[0]
hobot = Connector(ns, l["data"]["port"])
# exit()

joy = Joy()

move = [0, 0, 0]
hob = {'en': False, 'grip': False, 'position': [0, 0, 0, 0, 0, 0]}

for x in range(1000):
    move[0] = joy.joystat['speed'] * joy.joystat['dy'] * 500
    move[1] = joy.joystat['speed'] * joy.joystat['dx'] * 500
    move[2] = joy.joystat['speed'] * joy.joystat['lx'] * 250

    hob['en'] = joy.joystat['hobot']
    hob['grip'] = joy.joystat['grip']

    hob['position'][0] = joy.joystat['x']
    hob['position'][1] = -joy.joystat['y']

    hob['position'][2] = joy.joystat['x']
    hob['position'][3] = -joy.joystat['y']

    if joy.joystat['spin'] > 0:
        hob['position'][4] = joy.joystat['spin']
        hob['position'][5] = 0
    else:
        hob['position'][4] = 0
        hob['position'][5] = -joy.joystat['spin']

    print(hob['position'])
    time.sleep(0.1)
    drive.set(move)
    hobot.set(hob)

joy.stop()
