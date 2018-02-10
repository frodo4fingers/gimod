#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.lines import Line2D
from .mplbase import MPLBase
import numpy as np


class SpanLine(MPLBase):
    """
    Provide the visualization for creating a PolyLine.
    """

    def __init__(self, parent=None):
        """
        Initialize all important variables for matplotlib drawing.

        Parameters
        ----------
        parent: :class:`~core.builder.Builder`
        """
        super(SpanLine, self).__init__(parent)
        self.parent = parent
        self.figure = parent.figure
        self.gimod = parent.parent
        # so far a work-around for avoiding getting 'NoneType' as pressed
        # button event while drawing with magnetized net
        if hasattr(self.parent, 'grid'):
            self.parent.grid.update()
        # dummy to be drawn and 'exported' later
        line, = self.figure.axis.plot([0], [0], c='lightblue')
        self.line = line
        # dummy line to portrait where the line will be
        motionLine, = self.figure.axis.plot([0], [0], c='white')
        self.motionLine = motionLine
        self.x = []
        self.y = []
        # counter for plotting a line when there two sets of coordinates
        self.clicker = -1
        # trigger the drawing process
        self.onPress = self.onPress

    def onPress(self, event):
        """Collect the event data to later pass on to the PolyLine."""
        if event.button is 1:
            if event.dblclick:  # stop line building on double click
                self.disconnect()
            # the helper line is only need while dragging
            self.motionLine.set_data([0], [0])
            # self.background = None
            self.motionLine.set_animated(False)
            self.x_p = event.xdata
            self.y_p = event.ydata
            # check if cursour was grapped by the magnetized grid
            if self.gimod.toolbar.acn_magnetizeGrid.isChecked():
                if self.parent.grid.x_r is not None:
                    self.x_p = self.parent.grid.x_p
                    self.y_p = self.parent.grid.y_p
            # snap current position to nearest node if magnetized
            # this will override the just collected event data
            if self.gimod.toolbar.acn_magnetizePoly.isChecked() is True:
                if self.parent.mp.x_p is not None:
                    self.x_p = self.parent.mp.x_p
                    self.y_p = self.parent.mp.y_p
            self.x.append(self.x_p)
            self.y.append(self.y_p)
            self.line.set_data(self.x, self.y)
            self.figure.canvas.draw()
            self.clicker += 1

    def onMotion(self, event):
        """Set the data of cursor motion to the helper line."""
        try:  # to draw this stuff
            self.motionLine.set_data(
                (self.x[-1], event.xdata), (self.y[-1], event.ydata))
            self.figure.canvas.restore_region(self.background)
            self.motionLine.axes.draw_artist(self.motionLine)
            self.figure.canvas.blit(self.motionLine.axes.bbox)
        except (AttributeError, IndexError, TypeError):
            pass

    def onRelease(self, event):
        """Reset the line and send the necessary data to build the PolyLine."""
        try:  # to drag the line with the cursor
            self.motionLine.set_animated(True)
            self.background = self.figure.canvas.copy_from_bbox(
                self.motionLine.axes.bbox)
            self.motionLine.axes.draw_artist(self.motionLine)
            self.figure.canvas.blit(self.motionLine.axes.bbox)
        except (IndexError, TypeError):
            pass
        if self.clicker > 0:
            self.line.set_data([0], [0])
            line = Line2D(
                [self.x[self.clicker - 1], self.x[self.clicker]],
                [self.y[self.clicker - 1], self.y[self.clicker]], marker='o', c='white', mfc='white', mec='white')
            self.parent.magnets.append(np.asarray(line.get_data()))
            self.parent.storeMPLPaths(line, ['Line',
                [self.x[self.clicker - 1], self.y[self.clicker - 1],
                self.x[self.clicker], self.y[self.clicker]]])
            # update the magnets
            if self.gimod.toolbar.acn_magnetizePoly.isChecked():
                self.parent.mp.plotMagnets()


if __name__ == '__main__':
    pass
