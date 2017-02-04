#!/usr/bin/env python
# encoding: UTF-8

""" class for tab with main model builder components """
from PyQt4 import QtGui
from pygimli.mplviewer import drawMesh
from pygimli.meshtools import polytools as plc
import numpy as np
from PyQt4 import QtGui

import SpanRectangle
import SpanLine
from SpanCircle import SpanCircle


class Builder(QtGui.QWidget):

    def __init__(self, plotWidget, parent=None):
        super(Builder, self).__init__(parent)
        self.figure = plotWidget
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

        self.setupUI()

        """ connect signals """
        self.acn_circle.triggered.connect(self.createPolyCircle)

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
        c = SpanCircle(self)
        c.connect()
        try:
            x, y, r = c.getValues()
            print(x, y, r)
        except AttributeError:
            pass

    def printCoordinates(self):
        print(self.x1, self.y1)
        print(self.x2, self.y2)


if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    builderWin = Builder()
    builderWin.show()
    sys.exit(builderWin.exec_())
