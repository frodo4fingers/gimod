#!/usr/bin/env python
# encoding: UTF-8

""" class for tab with main model builder components """
from PyQt4 import QtGui
from pygimli.mplviewer import drawMesh
from pygimli.meshtools import polytools as plc
import numpy as np


class Builder():

    # def __init__(self, plotWidget, parent=None):
    def __init__(self, plotWidget, table, type_):
        # stuff
        # super(Builder, self).__init__(parent)
        self.plotWidget = plotWidget
        self.table = table
        self.type = type_
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
        self.clicked = 1
        self.cid_p = self.plotWidget.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.plotWidget.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.plotWidget.canvas.mpl_connect("button_release_event", self.onRelease)
        # self.plotWidget.canvas.draw()

    def disconnect(self):
        self.plotWidget.canvas.mpl_disconnect(self.cid_p)
        self.plotWidget.canvas.mpl_disconnect(self.cid_m)
        self.plotWidget.canvas.mpl_disconnect(self.cid_r)

    def getPoly(self):
        return self.poly, self.table

    def distance(self):
        return round(np.sqrt((self.x_m - self.x_p)**2 + (self.y_m - self.y_p)**2), 2)

    def onPress(self, event):
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
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

            if self.type == "circle":
                self.drawCircle()
            elif self.type == "rectangle":
                self.drawRectangle()
            elif self.type == "world":
                self.drawWorld()
            elif self.type == "line":
                self.drawLine()
            # set line empty to remove from view
            self.line.set_data([0], [0])
            self.line.axes.draw_artist(self.line)
            # draw gimli circle
            drawMesh(self.plotWidget.axis, self.poly, fitView=False)
            # set back variables
            self.line.set_animated(False)
            self.background = None
            self.plotWidget.canvas.draw()

            self.fillTable()

        except AttributeError:
            pass

    def changeType(self, type_):
        """
            called from mainwindow to change type of polygon so the class wont
            be called a scnd time
        """
        self.type = type_

    def drawCircle(self):
        """
            draw simple circle with polytools
        """
        if self.clicked > 1:
            # FIXME!!!!: der zeichnet alte polys übereinander... zu sehen an der fetter werdenden schrift ---> vllt alles über n dict?
            self.poly = plc.mergePLC([self.poly, plc.createCircle(pos=(self.x_p, self.y_p), segments=12, radius=self.distance(), marker=self.clicked)])
        else:
            self.poly = plc.createCircle(pos=(self.x_p, self.y_p), segments=12, radius=self.distance(), marker=self.clicked)

    def drawRectangle(self):
        """
            draw simple rectangle with polytools
            >>> kannweg5/8
        """
        if self.clicked > 1:
            self.poly = plc.mergePLC([self.poly, plc.createRectangle(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.clicked)])
        else:
            self.poly = plc.createRectangle(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.clicked)

    def drawWorld(self):
        """
            draw world where every other polygon will be in
        """
        if self.clicked > 1:
            self.poly = plc.mergePLC([self.poly, plc.createWorld(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.clicked)])
        else:
            self.poly = plc.createWorld(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.clicked)

    def drawLine(self):
        """
            draw line.. *duh*
        """
        if self.clicked > 1:
            self.poly = plc.mergePLC([self.poly, plc.createLine(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], segments=3, boundaryMarker=1)])
        else:
            self.poly = plc.createLine(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], segments=3, boundaryMarker=1)

    def drawPolygon(self):
        """
            function where the clicked polygon is assembled
            >>> kannweg2
        """

    # TODO: def redrawTable(self):

    def fillTable(self):
        """
            for construction: header labels >>>
            "Type", "x0", "y0", "x1", "y1", "Radius", "Segments", "Start", "End", "Marker", "Area", "Boundary", "Left?", "Hole?", "Closed?"
        """
        # update table on release
        self.table.setColumnCount(self.clicked)
        col = self.clicked - 1
        # insert poly type... circle/world/rectangle/hand
        self.table.setItem(0, col, QtGui.QTableWidgetItem(self.type))

        # if self.type == "circle":
        # insert position
        self.table.setItem(1, col, QtGui.QTableWidgetItem(str(round(self.x_p, 2))))
        self.table.setItem(2, col, QtGui.QTableWidgetItem(str(round(self.y_p, 2))))

        if self.type == "rectangle" or self.type == "world" or self.type == "line":
            self.table.setItem(3, col, QtGui.QTableWidgetItem(str(round(self.x_r, 2))))
            self.table.setItem(4, col, QtGui.QTableWidgetItem(str(round(self.y_r, 2))))

        if self.type == "circle":
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(12)
            spx_segments.setMinimum(3)
            self.table.setCellWidget(6, col, spx_segments)

        if self.type == "line":
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(3)
            spx_segments.setMinimum(3)
            self.table.setCellWidget(6, col, spx_segments)

        if self.type == "circle":
            # insert radius
            spx_radius = QtGui.QDoubleSpinBox()
            spx_radius.setSingleStep(0.01)
            spx_radius.setValue(self.distance())
            self.table.setCellWidget(5, col, spx_radius)
            # insert start
            spx_start = QtGui.QDoubleSpinBox()
            spx_start.setValue(0.00)
            spx_start.setMinimum(0.00)
            spx_start.setSingleStep(0.01)
            spx_start.setMaximum(2*np.pi)
            self.table.setCellWidget(7, col, spx_start)
            # insert end
            spx_end = QtGui.QDoubleSpinBox()
            spx_end.setValue(2*np.pi)
            spx_end.setMinimum(0.00)
            spx_end.setSingleStep(0.01)
            spx_end.setMaximum(2*np.pi)
            self.table.setCellWidget(8, col, spx_end)

        if not self.type == "line":
            # insert marker
            for k in range(self.clicked):
                a = QtGui.QComboBox(self.table)
                [a.addItem(str(m+1)) for m in range(self.clicked)]
                a.setCurrentIndex(k)
                self.table.setCellWidget(9, k, a)
            # insert area
            spx_area = QtGui.QDoubleSpinBox()
            spx_area.setSingleStep(0.01)
            spx_area.setValue(0.00)
            spx_area.setMinimum(0.00)
            self.table.setCellWidget(10, col, spx_area)

        if not self.type == "world":
            # insert boundary marker
            self.table.setItem(11, col, QtGui.QTableWidgetItem(str(1)))
            # insert left direction
            cbx_isLeft = QtGui.QComboBox()
            cbx_isLeft.addItem("False")
            cbx_isLeft.addItem("True")
            self.table.setCellWidget(12, col, cbx_isLeft)

        if self.type != "world" and self.type != "line":
            # insert is hole
            cbx_isHole = QtGui.QComboBox()
            cbx_isHole.addItem("False")
            cbx_isHole.addItem("True")
            self.table.setCellWidget(13, col, cbx_isHole)
            # insert is closed
            cbx_isClosed = QtGui.QComboBox()
            cbx_isClosed.addItem("False")
            cbx_isClosed.addItem("True")
            self.table.setCellWidget(14, col, cbx_isClosed)

        self.table.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.table.resizeColumnsToContents()

        # iterate marker counter
        self.clicked += 1
