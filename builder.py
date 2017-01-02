#!/usr/bin/env python
# encoding: UTF-8

""" class for tab with main model builder components """
from PyQt4 import QtGui
from pygimli.mplviewer import drawMesh
from pygimli.meshtools import polytools as plc
import numpy as np


# class Builder(QtGui.QWidget):
class Builder():

    def __init__(self, plotWidget, parent=None):
        # stuff
        # super(Builder, self).__init__(parent)
        self.plotWidget = plotWidget
        # introduce empty line to start with
        line, = self.plotWidget.axis.plot([0], [0])
        self.line = line
        self.background = None
        self.onPress = self.onPress
        # self.initLayout()

        # """ connect buttons """
        # self.btn_circle.clicked.connect(self.circleHandler)

    # def initLayout(self):
    #     """
    #         initiate the widget
    #     """
    #     self.btn_circle = QtGui.QPushButton("C")
    #     # self.btn_circle.setToolTip("create a circle")
    #     self.btn_circle.setStatusTip("HELP: create a circle and specify parameters by right click")
    #     self.btn_circle.setCheckable(True)
    #     self.btn_circle.setFixedSize(30, 30)
    #
    #     buttons_grid = QtGui.QGridLayout()
    #     buttons_grid.addWidget(self.btn_circle, 1, 0, 1, 1)
    #
    #     builder_widget = QtGui.QWidget(self)
    #     builder_widget.setLayout(buttons_grid)

    # def circleHandler(self):
    #     """
    #         draw a gimli circle
    #         ...you get here by clicking the button "btn_circle"
    #     """
    #     if self.btn_circle.isChecked() is True:
    #         # clicked - iterate over clicks for marker counting
    #         self.clicked = 1
    #         self.cid_p = self.plotWidget.canvas.mpl_connect("button_press_event", self.onPress)
    #         self.cid_m = self.plotWidget.canvas.mpl_connect("motion_notify_event", self.onMotion)
    #         self.cid_r = self.plotWidget.canvas.mpl_connect("button_release_event", self.onRelease)
    #         self.plotWidget.axis.set_xlim([-10, 10])
    #         self.plotWidget.axis.set_ylim([-10, 10])
    #         self.plotWidget.canvas.draw()
    #     else:
    #         self.plotWidget.canvas.mpl_disconnect(self.cid_p)
    #         self.plotWidget.canvas.mpl_disconnect(self.cid_m)
    #         self.plotWidget.canvas.mpl_disconnect(self.cid_r)

    def connect(self):
        print("connect")
        self.clicked = 1
        self.cid_p = self.plotWidget.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.plotWidget.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.plotWidget.canvas.mpl_connect("button_release_event", self.onRelease)
        self.plotWidget.axis.set_xlim([-10, 10])
        self.plotWidget.axis.set_ylim([-10, 10])
        self.plotWidget.canvas.draw()

    def disconnect(self):
        self.plotWidget.canvas.mpl_disconnect(self.cid_p)
        self.plotWidget.canvas.mpl_disconnect(self.cid_m)
        self.plotWidget.canvas.mpl_disconnect(self.cid_r)

    def getPoly(self):
        return self.poly

    def distance(self):
        return round(np.sqrt((self.x_m - self.x_p)**2 + (self.y_m - self.y_p)**2), 2)

    def onPress(self, event):
        print("pressed")
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
            # print("press", self.x_p, self.y_p)
            self.line.set_animated(True)
            self.plotWidget.canvas.draw()
            self.background = self.plotWidget.canvas.copy_from_bbox(self.line.axes.bbox)
            self.line.axes.draw_artist(self.line)
            self.plotWidget.canvas.blit(self.line.axes.bbox)

    def onMotion(self, event):
        if event.inaxes != self.line.axes: return
        try:
            self.x_m = event.xdata
            self.y_m = event.ydata
            self.line.set_data([self.x_p, self.x_m], [self.y_p, self.y_m])
            # TODO: den radius am ansatzpunkt anzeigen
            # self.plotWidget.axis.annotate(self.distance(), xy=(self.x_p, self.y_p))

            self.plotWidget.canvas.restore_region(self.background)
            self.line.axes.draw_artist(self.line)
            self.plotWidget.canvas.blit(self.line.axes.bbox)

        except (AttributeError, TypeError):
            pass

    def onRelease(self, event):
        try:
            self.x_r = event.xdata
            self.y_r = event.ydata
            # create gimli circle
            if self.clicked > 1:
                self.poly = plc.mergePLC([self.poly, plc.createCircle(pos=(self.x_p, self.y_p), segments=6, radius=self.distance(), marker=self.clicked)])
            else:
                self.poly = plc.createCircle(pos=(self.x_p, self.y_p), segments=6, radius=self.distance(), marker=self.clicked)
            # iterate marker counter
            self.clicked += 1
            # set line empty to remove from view
            self.line.set_data([0], [0])
            self.line.axes.draw_artist(self.line)
            # draw gimli circle
            drawMesh(self.plotWidget.axis, self.poly, fitView=False)
            # set back variables
            self.line.set_animated(False)
            self.background = None
            self.plotWidget.canvas.draw()

        except AttributeError:
            pass

# TODO: das self.poly zurückgeben an das hauptfenster!!!!!!!!!!
# BUG: ON... poly machen.. OFF.. ON.. poly machen. beide haben marker 1 logischerweise. also entweder das obige TODO klarmachen, sodass die einzelnen polygone kontrolliert werden oder denk dir was anderes aus! :-)
