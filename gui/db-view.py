#!/usr/bin/env python

# from PyQt5.QtCore import QFileInfo
try:
    import ujson as json
except:
    print('ujson not found, using json')
    import json

import zmq
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QListWidget,
                             QTabWidget, QVBoxLayout, QWidget, QPushButton, QCalendarWidget, QFileDialog)


class TabDialog(QDialog):
    def __init__(self, parent=None):
        super(TabDialog, self).__init__(parent)

        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REQ)

        self.showFullScreen()
        self.tabW = QTabWidget()

        self.Locator = SelectLocator(self)
        self.Session = SelectSession(self)
        self.View = ViewData(self)
        self.tabW.addTab(self.Locator, "Select Locator")
        self.tabW.addTab(self.Session, "Select Session")
        self.tabW.addTab(self.View, "View Data")

        self.tabW.setTabEnabled(1, False)
        self.tabW.setTabEnabled(2, False)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabW)
        self.setLayout(mainLayout)

        self.setWindowTitle("Tab Dialog")


class SelectLocator(QWidget):
    def doConnect(self):
        i = self.locatorW.selectedItems()

        if (i):
            item = i[0]
            addr = item.text()
            try:
                port = 15701
                self.glob.socket.connect("tcp://" + addr + ":" + str(port))
                self.glob.tabW.setTabEnabled(1, True)
                self.glob.tabW.setCurrentIndex(1)
                self.glob.Session.update()
            except Exception as e:
                print(e)

    def __init__(self, main, parent=None):
        super(SelectLocator, self).__init__(parent)
        self.glob = main
        mainLayout = QVBoxLayout()

        self.locatorW = QListWidget()
        locators = ['127.0.0.1']  # , '192.168.6.111']
        self.locatorW.insertItems(0, locators)

        btnW = QPushButton('Connect')
        btnW.clicked.connect(self.doConnect)

        mainLayout.addWidget(self.locatorW)
        mainLayout.addWidget(btnW)

        # mainLayout.addStretch(0)
        self.setLayout(mainLayout)


class SelectSession(QWidget):
    def update(self):
        self.glob.socket.send_json(dict(action='listsessions'))
        res = self.glob.socket.recv_json()
        self.dates = set()

        self.lst.insertItems(0, [d + " " + name for d, name in res])
        for d, n in res:
            self.dates.add(d.split(' ')[0])

        format = QtGui.QTextCharFormat()
        format.setForeground(QtCore.Qt.blue)
        format.setBackground(QtCore.Qt.lightGray)
        import datetime

        for d in self.dates:
            dt = datetime.datetime.strptime(d,
                                            "%Y-%m-%d")  # datetime.datetime.strptime(str(_now), "%Y-%m-%d %H:%M:%S.%f")
            print(dt)
            self.cal.setDateTextFormat(dt.date(), format)

    def goto(self):
        i = self.lst.selectedItems()
        if (i):
            item = i[0]
            import datetime
            dt = datetime.datetime.strptime(item.text().split(" ")[0], "%Y-%m-%d")
            self.cal.setSelectedDate(dt.date())

    def doExport(self):
        i = self.lst.selectedItems()
        for x in i:
            txt = x.text()
            d, t, n = txt.split(" ")

            # mk query for n


            fname = QFileDialog.getSaveFileName(self, 'Savefile', './', "raw json(*.json);; exel tables(*.csv)")

            self.glob.socket.send_json(dict(action='getdata', name=n, limit=1000))
            res = self.glob.socket.recv_json()

            if ('.csv' == fname[0][-4:]):
                print(res[0])
                f = open(fname[0], "w")
                for i, t in enumerate(res[0][0]):
                    f.write('time {0};'.format(i))
                f.write("\n")
                for r in res:
                    for r2 in r[0]:
                        f.write('{0};'.format(r2))
                    try:
                        if isinstance(r[1], list):
                            for r2 in r[1]:
                                f.write('{0};'.format(str(r2)))
                        else:
                            f.write(str(r[1]))

                    except:
                        f.write(str(r[1]))
                    f.write("\n")








            else:

                f = open(fname[0], "w")
                f.write(json.dumps(res))
                f.close()

    def __init__(self, main, parent=None):
        super(SelectSession, self).__init__(parent)
        self.glob = main

        mainLayout = QVBoxLayout()

        self.cal = QCalendarWidget()
        self.export = QPushButton('CSV export')
        self.cal.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.lst = QListWidget()
        self.lst.clicked.connect(self.goto)

        mainLayout.addWidget(self.cal)
        mainLayout.addWidget(self.lst)

        mainLayout.addWidget(self.export)

        self.export.clicked.connect(self.doExport)
        mainLayout.addStretch(2)

        self.setLayout(mainLayout)


class ViewData(QWidget):
    def __init__(self, main, parent=None):
        super(ViewData, self).__init__(parent)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    tabdialog = TabDialog()
    tabdialog.show()
    sys.exit(app.exec_())
