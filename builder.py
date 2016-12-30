#!/usr/bin/env python
# encoding: UTF-8

""" class for tab with main model builder components """
from PyQt4 import QtGui
from pygimli.mplviewer import drawMesh
from pygimli.meshtools import polytools as plc
import pygimli as pg

class Builder(QtGui.QWidget):

    def __init__(self, plotWidget, parent=None):
        # stuff
        super(Builder, self).__init__(parent)
        self.plotWidget = plotWidget
        self.initLayout()

        """ connect buttons """
        self.btn_circle.clicked.connect(self.circleHandler)

    def initLayout(self):
        """
            initiate the widget
        """

        self.btn_circle = QtGui.QPushButton("A")
        # self.btn_circle.setToolTip("create a circle")
        self.btn_circle.setStatusTip("TIP: create a circle and specify parameters by right click")
        self.btn_circle.setCheckable(True)
        self.btn_circle.setFixedSize(30, 30)

        buttons_grid = QtGui.QGridLayout()
        buttons_grid.addWidget(self.btn_circle, 1, 0, 1, 1)

        builder_widget = QtGui.QWidget(self)
        builder_widget.setLayout(buttons_grid)

    def circleHandler(self):
        """
            draw a gimli circle
        """
        if self.btn_circle.isChecked() is True:
            # click iterator for counting markers
            self.clicked = 1
            self.cid = self.plotWidget.canvas.mpl_connect("button_press_event", self.onClick)
            self.x = self.plotWidget.axis.get_xlim()
            self.y = self.plotWidget.axis.get_ylim()
            # c = plc.createCircle(pos=(self.x_, self.y_))
            # self.plotWidget.axis.plot(400, 200, "ro")
            # self.drawPolyStuff(c)
        else:
            self.plotWidget.canvas.mpl_disconnect(self.cid)

    def drawPolyStuff(self, poly):
        drawMesh(self.plotWidget.axis, poly)
        self.plotWidget.axis.set_xlim(self.x)
        self.plotWidget.axis.set_ylim(self.y)
        self.plotWidget.canvas.draw()
        # pg.show(poly, ax=self.plotWidget.axis, )

    def onClick(self, event):
        self.x_ = event.xdata
        self.y_ = event.ydata
        print(self.clicked, self.x_, self.y_)
        if self.clicked > 1:
            self.poly = plc.mergePLC([self.poly, plc.createCircle(pos=(self.x_, self.y_), segments=6, radius=self.x[1]/10, marker=self.clicked)])
        else:
            self.poly = plc.createCircle(pos=(self.x_, self.y_), segments=6, radius=self.x[1]/10, marker=self.clicked)

        self.clicked += 1
        self.drawPolyStuff(self.poly)
