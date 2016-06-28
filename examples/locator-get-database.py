from __future__ import unicode_literals

import zmq

ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
ip = '127.0.0.1'
port = 15701
socket.connect("tcp://" + ip + ":" + str(port))

socket.send_json(dict(action='list'))
d = socket.recv_json()
print(d)

socket.send_json(dict(action='getdata', limit=100, name='wifi'))
data = socket.recv_json()

for t, d in data:
    print(t[-1], d)
# data = [val for times, val in d['data']]
from pprint import pprint

pprint(d)
import sys
import os
import matplotlib

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        global socket

        socket.send_json(dict(action='getdata', limit=1000, name='wifi'))
        data = socket.recv_json()
        t1 = []
        t2 = []
        t3 = []
        d1 = []
        for t, d in data:
            t1.append(t[-1])
            t2.append(t[-2])
            t3.append(t2[-1] - t1[-1])
            d1.append(d)
        # self.axes.plot(t1, 'r')
        # self.axes.plot(t2, 'g')
        self.axes.plot(t3, 'b')
        # self.axes.plot(a2, 'r')
        self.draw()
        import time
        print(time.time())


class ApplicationWindow(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QVBoxLayout(self.main_widget)

        dc = MyDynamicMplCanvas(self.main_widget, width=7, height=4, dpi=100)

        l.addWidget(dc)

        self.main_widget.setFocus()


qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
# qApp.exec_()
