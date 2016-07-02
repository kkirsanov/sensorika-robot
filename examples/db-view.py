#!/usr/bin/env python

# from PyQt5.QtCore import QFileInfo
import zmq
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QListWidget,
                             QTabWidget, QVBoxLayout, QWidget, QPushButton, QCalendarWidget)


class TabDialog(QDialog):
    def __init__(self, parent=None):
        super(TabDialog, self).__init__(parent)

        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REQ)

        # self.socket.connect("tcp://" + addr + ":15701")

        # socket.send_json(dict(action='list'))
        # d = socket.recv_json()
        # print(d)
        self.showFullScreen()
        self.tabW = QTabWidget()
        # self.tabW.setMinimumWidth(740)
        # self.tabW.setMinimumHeight(500)
        self.tabW.addTab(SelectLocator(self), "Select Locator")
        self.tabW.addTab(SelectSession(self), "Select Session")
        self.tabW.addTab(ViewData(self), "View Data")

        self.tabW.setTabEnabled(1, False)
        self.tabW.setTabEnabled(2, False)

        # buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # buttonBox.accepted.connect(self.accept)
        # buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabW)
        # mainLayout.addWidget(buttonBox)
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
            except Exception as e:
                print(e)

    def __init__(self, main, parent=None):
        super(SelectLocator, self).__init__(parent)
        self.glob = main
        mainLayout = QVBoxLayout()

        self.locatorW = QListWidget()
        locators = ['127.0.0.1', '192.168.6.111']
        self.locatorW.insertItems(0, locators)

        btnW = QPushButton('Connect')
        btnW.clicked.connect(self.doConnect)

        mainLayout.addWidget(self.locatorW)
        mainLayout.addWidget(btnW)

        # mainLayout.addStretch(0)
        self.setLayout(mainLayout)


class SelectSession(QWidget):
    def __init__(self, main, parent=None):
        super(SelectSession, self).__init__(parent)
        self.glob = main

        mainLayout = QVBoxLayout()

        """
        self.locatorW = QListWidget()
        locators = ['127.0.0.1', '192.168.6.111']
        self.locatorW.insertItems(0, locators)

        btnW = QPushButton('Connect')
        btnW.clicked.connect(self.doConnect)

        mainLayout.addWidget(self.locatorW)
        mainLayout.addWidget(btnW)

        """
        self.cal = QCalendarWidget()
        import datetime
        format = QtGui.QTextCharFormat()
        # format.setForeground(QtCore.Qt.blue)
        format.setBackground(QtCore.Qt.blue)
        self.cal.setDateTextFormat(datetime.date(2016, 7, 1), format)
        mainLayout.addWidget(self.cal)
        mainLayout.addStretch(2)
        self.setLayout(mainLayout)


class ViewData(QWidget):
    def __init__(self, main, parent=None):
        super(ViewData, self).__init__(parent)
        self.glob = main


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    tabdialog = TabDialog()
    tabdialog.show()
    sys.exit(app.exec_())
