import threading
import time

from examples.sensorika.inputs import get_gamepad


class Joy(threading.Thread):
    def __init__(self, *a, **k):
        self.Estop = threading.Event()
        super(Joy, self).__init__()
        self.thread = self.start()
        self.joystat = dict(x=0, y=0, speed=0, grip=False, hobot=False, lx=0, ly=0, dx=0, dy=0)

    def run(self):
        while not self.Estop.is_set():
            events = get_gamepad()
            print(self.joystat)
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


j = Joy()

time.sleep(100)
j.stop()
