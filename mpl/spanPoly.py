#!/usr/bin/env python
# encoding: UTF-8

from matplotlib.patches import Polygon
from .mplbase import MPLBase


class SpanPoly(MPLBase):
    """Provide the visualization for creating a manually drawn Polygon."""

    def __init__(self, parent=None):
        """
        Initialize all important variables for matplotlib drawing.

        Parameters
        ----------
        parent: :class:`core.builder.Builder`
        """
        super(SpanPoly, self).__init__(parent)
        self.gimod = parent.parent
        self.parent = parent
        self.figure = parent.figure
        self.resetAllComponents()

    def resetAllComponents(self):
        """
        Set helper line, the line that assembles Polygon parts and the storages
        lists for establishing those lines.
        """
        # helper line to draw between clicks
        motionLine, = self.figure.axis.plot([0], [0], c='lightblue')
        self.motionLine = motionLine
        # actual line that will be staying and form the pre-poly
        line, = self.figure.axis.plot([0], [0], c='white')
        self.line = line
        # store the clicked data points in lists
        self.x = []
        self.y = []
        self.background = None
        self.onPress = self.onPress

    def onPress(self, event):
        """
        Store the data of first click and enable the drawing of the helper
        line. Clsoing the polygon happens with doubleclick that sends the x and
        y values to the builder.
        """
        # reset line for next click
        self.motionLine.set_data([0], [0])
        self.background = None
        self.motionLine.set_animated(False)
        self.figure.canvas.draw()

        if event.button is 1:  # left mouse button
            if event.dblclick:  # close polygon
                # self.parent.printPolygon(
                #     [[self.x[i], self.y[i]] for i in range(len(self.x))])
                poly = Polygon([[self.x[i], self.y[i]] for i in range(len(self.x))])
                self.parent.storeMPLPaths(poly, ['Polygon',
                    [[self.x[i], self.y[i]] for i in range(len(self.x))]])
                # reset the necessary components
                self.resetAllComponents()

            else:  # append point to polygon
                self.x_p = event.xdata
                self.y_p = event.ydata
                # snap current position to nearest node if magnetized
                # this will override the just collected event data
                if self.gimod.toolbar.acn_magnetizePoly.isChecked():
                    if self.parent.mp.x_p is not None:
                        self.x_p = self.parent.mp.x_p
                        self.y_p = self.parent.mp.y_p
                self.x.append(self.x_p)
                self.y.append(self.y_p)
                # draw the edge between two points
                self.line.set_data(self.x, self.y)
                self.figure.canvas.draw()

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
        """Reset the data of the motionLine to draw it from scratch."""
        try:  # to drag the line with the cursor
            self.motionLine.set_animated(True)
            self.background = self.figure.canvas.copy_from_bbox(
                self.motionLine.axes.bbox)
            self.motionLine.axes.draw_artist(self.motionLine)
            self.figure.canvas.blit(self.motionLine.axes.bbox)
        except (IndexError, TypeError):
            pass


if __name__ == '__main__':
    pass
