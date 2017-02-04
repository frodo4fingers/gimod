#!/usr/bin/env python
# encoding: UTF-8

""" class for tab with main model builder components """
from PyQt4 import QtGui
from pygimli.mplviewer import drawMesh
from pygimli.meshtools import polytools as plc
import numpy as np
from PyQt4 import QtGui

from SpanRectangle import SpanRectangle
import SpanLine
from SpanCircle import SpanCircle


class Builder(QtGui.QWidget):

    def __init__(self, plotWidget, parent=None):
        super(Builder, self).__init__(parent)
        self.figure = plotWidget
        self.marker = 1
        self.polys = []
        print("IIIIIINNNNNIIIIIIIT")

        self.setupUI()

        """ connect signals """
        self.acn_circle.triggered.connect(self.createPolyCircle)
        self.acn_rectangle.triggered.connect(self.createPolyRectangle)

    def setupUI(self):
        """
            composing the layout for the tab
        """
        # polytool buttons
        self.grp_polyTools = QtGui.QActionGroup(self)

        self.acn_world = QtGui.QAction("world", self.grp_polyTools)
        self.acn_world.setText("W")
        self.acn_world.setToolTip("create a world")
        self.acn_world.setCheckable(True)

        self.acn_rectangle = QtGui.QAction("rectangle", self.grp_polyTools)
        self.acn_rectangle.setText("R")
        self.acn_rectangle.setToolTip("create a rectangle")
        self.acn_rectangle.setCheckable(True)

        self.acn_circle = QtGui.QAction("circle", self.grp_polyTools)
        self.acn_circle.setText("C")
        self.acn_circle.setToolTip("create a circle")
        self.acn_circle.setCheckable(True)

        self.acn_line = QtGui.QAction("line", self.grp_polyTools)
        self.acn_line.setText("L")
        self.acn_line.setToolTip("create a line")
        self.acn_line.setCheckable(True)

        tb = QtGui.QToolBar()
        tb.setMovable(False)
        tb.addAction(self.acn_world)
        tb.addAction(self.acn_rectangle)
        tb.addAction(self.acn_circle)
        tb.addAction(self.acn_line)

        # parameter table for different polygons
        self.polys_table = QtGui.QTableWidget(self)
        self.polys_table.setRowCount(15)
        self.polys_table.setVerticalHeaderLabels(("Type", "x0", "y0", "x1", "y1", "Radius", "Segments", "Start", "End", "Marker", "Area", "Boundary", "Left?", "Hole?", "Closed?"))

        # form the layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tb)
        vbox.addWidget(self.polys_table)
        self.setLayout(vbox)

    def createPolyCircle(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanCircle(self)
        self.span.connect()

    def createPolyRectangle(self):
        try:
            self.span.disconnect()
        except AttributeError:
            pass
        self.span = SpanRectangle(self)
        self.span.connect()

    def printCoordinates(self, x1, y1, x2, y2, form):

        self.x_p = x1
        self.y_p = y1
        self.x_r = x2
        self.y_r = y2
        self.form = form

        print(self.form)
        self.drawPoly()

    def drawPoly(self):

        if self.form == "circle":
            self.polys.append(plc.createCircle(pos=(self.x_p, self.y_p), segments=12, radius=self.x_r, marker=self.marker))

        elif self.form == "rectangle":
            self.polys.append(plc.createRectangle(start=[self.x_p, self.y_p], end=[self.x_r, self.y_r], marker=self.marker))

        self.poly = plc.mergePLC(self.polys)
        self.figure.axis.cla()

        drawMesh(self.figure.axis, self.poly, fitView=False)
        self.figure.canvas.draw()

        self.fillTable()

    def fillTable(self):
        """
            for construction: header labels >>>
            "Type", "x0", "y0", "x1", "y1", "Radius", "Segments", "Start", "End", "Marker", "Area", "Boundary", "Left?", "Hole?", "Closed?"
        """
        print("table", self.marker, self.form)
        # update table on release
        self.polys_table.setColumnCount(self.marker)
        col = self.marker - 1
        # insert poly type... circle/world/rectangle/hand
        self.polys_table.setItem(0, col, QtGui.QTableWidgetItem(self.form))

        # if self.form == "circle":
        # insert position
        self.polys_table.setItem(1, col, QtGui.QTableWidgetItem(str(round(self.x_p, 2))))
        self.polys_table.setItem(2, col, QtGui.QTableWidgetItem(str(round(self.y_p, 2))))

        if self.form == "rectangle" or self.form == "world" or self.form == "line":
            self.polys_table.setItem(3, col, QtGui.QTableWidgetItem(str(round(self.x_r, 2))))
            self.polys_table.setItem(4, col, QtGui.QTableWidgetItem(str(round(self.y_r, 2))))

        if self.form == "circle":
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(12)
            spx_segments.setMinimum(3)
            self.polys_table.setCellWidget(6, col, spx_segments)

        if self.form == "line":
            # insert segments
            spx_segments = QtGui.QSpinBox()
            spx_segments.setValue(3)
            spx_segments.setMinimum(3)
            self.polys_table.setCellWidget(6, col, spx_segments)

        if self.form == "circle":
            # insert radius
            spx_radius = QtGui.QDoubleSpinBox()
            spx_radius.setSingleStep(0.01)
            spx_radius.setValue(self.x_r)
            self.polys_table.setCellWidget(5, col, spx_radius)
            # insert start
            spx_start = QtGui.QDoubleSpinBox()
            spx_start.setValue(0.00)
            spx_start.setMinimum(0.00)
            spx_start.setSingleStep(0.01)
            spx_start.setMaximum(2*np.pi)
            self.polys_table.setCellWidget(7, col, spx_start)
            # insert end
            spx_end = QtGui.QDoubleSpinBox()
            spx_end.setValue(2*np.pi)
            spx_end.setMinimum(0.00)
            spx_end.setSingleStep(0.01)
            spx_end.setMaximum(2*np.pi)
            self.polys_table.setCellWidget(8, col, spx_end)

        if not self.form == "line":
            # insert marker
            for k in range(self.marker):
                a = QtGui.QComboBox(self.polys_table)
                [a.addItem(str(m+1)) for m in range(self.marker)]
                a.setCurrentIndex(k)
                self.polys_table.setCellWidget(9, k, a)
            # insert area
            spx_area = QtGui.QDoubleSpinBox()
            spx_area.setSingleStep(0.01)
            spx_area.setValue(0.00)
            spx_area.setMinimum(0.00)
            self.polys_table.setCellWidget(10, col, spx_area)

        if not self.form == "world":
            # insert boundary marker
            self.polys_table.setItem(11, col, QtGui.QTableWidgetItem(str(1)))
            # insert left direction
            cbx_isLeft = QtGui.QComboBox()
            cbx_isLeft.addItem("False")
            cbx_isLeft.addItem("True")
            self.polys_table.setCellWidget(12, col, cbx_isLeft)

        if self.form != "world" and self.form != "line":
            # insert is hole
            cbx_isHole = QtGui.QComboBox()
            cbx_isHole.addItem("False")
            cbx_isHole.addItem("True")
            self.polys_table.setCellWidget(13, col, cbx_isHole)
            # insert is closed
            cbx_isClosed = QtGui.QComboBox()
            cbx_isClosed.addItem("False")
            cbx_isClosed.addItem("True")
            self.polys_table.setCellWidget(14, col, cbx_isClosed)

        self.polys_table.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.polys_table.resizeColumnsToContents()

        # iterate marker counter
        self.marker += 1
        print("table", self.marker)


if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    builderWin = Builder()
    builderWin.show()
    sys.exit(builderWin.exec_())
