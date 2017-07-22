#!/usr/bin/env python
# encoding: UTF-8

from . import MagnetizePolygons

class Helper():
    """
    Establish helper functions for graphical sugar.
    """

    def __init__(self, parent=None):
        """."""
        self.figure = parent.plotWidget

    def toggleGrid(self):
        if self.gridClicked is True:
            self.figure.axis.grid()
            self.gridClicked = False
        else:
            self.figure.axis.grid(False)
            self.gridClicked = True
            self.acn_gridToggle.setChecked(False)
        self.figure.canvas.draw()

    def magnetizeGrid(self):
        if self.magnetize is True:
            self.figure.axis.grid()
            self.magnetize = False
        else:
            self.figure.axis.grid(False)
            self.magnetize = True
            self.acn_magnetizeGrid.setChecked(False)
        self.figure.canvas.draw()

    def magnetizePoly(self):
        if self.mPolyClicked is True:
            x = []
            y = []
            x, y = self.getNodes()

            self.mp = MagnetizePolygons(self, x, y)
            self.mp.connect()
            # HACK: against flickering and false data while spanning:
            self.span.disconnect()
            self.span.connect()
            self.mPolyClicked = False
        else:
            self.mp.disconnect()
            self.figure.axis.grid(False)
            self.mPolyClicked = True
            self.acn_magnetizeGrid.setChecked(False)
        self.figure.canvas.draw()

    def getNodes(self):
        arr = self.poly.positions()
        x = list(pg.x(arr))
        y = list(pg.y(arr))

        return x, y
