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
            for event in events:
                # if event.code not in ('ABS_Y', 'ABS_X', 'SYN_REPORT'):
                # print(self.joystat)
                if event.ev_type == 'Absolute':
                    if event.code == 'ABS_HAT0X':
                        self.joystat['dx'] = event.state
                    if event.code == 'ABS_HAT0Y':
                        self.joystat['dy'] = event.state
                    if event.code == 'ABS_X':
                        self.joystat['x'] = -(512 - event.state) / 512.0
                        continue
                    if event.code == 'ABS_Y':
                        self.joystat['y'] = (512 - event.state) / 512.0
                        continue
                    if event.code == 'ABS_THROTTLE':
                        self.joystat['speed'] = event.state

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
                        if event.state == 1:
                            self.joystat['ly'] = 1
                        else:
                            self.joystat['ly'] = 0
                        continue
                    if event.code == 'UNKNOWN_302':
                        if event.state == 1:
                            self.joystat['ly'] = -1
                        else:
                            self.joystat['ly'] = 0
                        continue
                    if event.code == 'BTN_BASE6':
                        if event.state == 1:
                            self.joystat['lx'] = -1
                        else:
                            self.joystat['lx'] = 0
                        continue
                    if event.code == 'UNKNOWN_301':
                        if event.state == 1:
                            self.joystat['lx'] = 1
                        else:
                            self.joystat['lx'] = 0
                        continue

                print(event.ev_type, event.code, event.state)

    def stop(self):
        self.Estop.set()


j = Joy()

time.sleep(100)
j.stop()
