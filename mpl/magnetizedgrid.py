from matplotlib.lines import Line2D
# from numpy import allclose
import numpy as np

try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtGui import QCursor
    from PyQt5.QtCore import Qt, QPoint

except ImportError:
    from PyQt4.QtQui import QCursor, QApplication, QWidget
    from PyQt4.QtCore import Qt, QPoint

import time


class MagnetizedGrid():
    """
    Everything the grid resembles is stored here. The drawing, the
    magnetization and 'catching' and the scalability.

    Note
    ----
    4me: scrolling with ctrl+g should increase/decrease the density of lines drawn

    Todo
    ----
    *[x] make grid
    *[x] make grid magnetized
    *[ ] make grid free scalable
    """

    def __init__(self, parent=None):
        """Initialize the important variables."""
        self.figure = parent.figure
        self.parent = parent  # builder
        self.gimod = parent.parent
        dot, = self.figure.axis.plot([], [], 'o', c='#ff0000')
        self.dot = dot
        self.grid()
        self.getCanvasHeight()
        self.onMotion = self.onMotion

    def getCanvasHeight(self):
        """."""
        _, self.height = self.figure.canvas.get_width_height()

    def connect(self):
        """."""
        self.cid_p = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cid_ae = self.figure.canvas.mpl_connect('axes_enter_event', self.axesEnter)
        self.cid_al = self.figure.canvas.mpl_connect('axes_leave_event', self.axesLeave)
        self.cid_r = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def axesLeave(self, event):
        QApplication.restoreOverrideCursor()

    def axesEnter(self, event):
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))

    def disconnect(self):
        """."""
        try:
            self.figure.canvas.mpl_disconnect(self.cid_p)
            self.figure.canvas.mpl_disconnect(self.cid_m)
            self.figure.canvas.mpl_disconnect(self.cid_ae)
            self.figure.canvas.mpl_disconnect(self.cid_al)
            self.figure.canvas.mpl_disconnect(self.cid_r)
        except AttributeError:
            # bc the grid might never be magnetized, thus not having any cid to disconnect
            pass

    def disable(self):
        """Disable the grid and reset the dot."""
        self.figure.axis.grid(False)
        self.dot = self.figure.axis.plot([], [], 'o', c='#ff0000')
        self.figure.canvas.draw()

    def grid(self):
        """Establish the grid and save the grid positions."""
        # set the actual grid
        self.figure.axis.grid()
        self.figure.canvas.draw()
        # get the axis ticks. returns a list of x,y-tuple
        x_ticks = [i.get_position()[0] for i in
            self.figure.axis.get_xticklabels()]
        y_ticks = [i.get_position()[1] for i in
            self.figure.axis.get_yticklabels()]

        # establish all cross sections as pixel position data
        self.crossings = []
        for x in x_ticks:
            for y in y_ticks:
                self.crossings.append(tuple(self.figure.axis.transData.transform((x, y))))

    def onPress(self, event):
        """Set the magnetic dot if somewhere near the grid ON PRESS."""
        if event.inaxes:
            try:
                dot, _ = self.vicinity(event.xdata, event.ydata)
            except TypeError:
                # no vicinity at all
                self.x_p = event.xdata
                self.y_p = event.ydata
            else:
                # if dot is not None:
                self.x_p = dot[0]
                self.y_p = dot[1]
                self._checkDot()
                self.dot.set_data(self.x_p, self.y_p)
                self.dot.set_animated(True)
                self.figure.canvas.draw()
                self.background = self.figure.canvas.copy_from_bbox(self.dot.axes.bbox)
                self.dot.axes.draw_artist(self.dot)
                self.figure.canvas.blit(self.dot.axes.bbox)

    def onMotion(self, event):
        """."""
        if event.inaxes:  # meaning within the plotting area
            self._checkDot()
            self.dot.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.dot.axes.bbox)
            self.dot.axes.draw_artist(self.dot)
            self.figure.canvas.blit(self.dot.axes.bbox)
            try:
                dot, color = self.vicinity(event.xdata, event.ydata)
                self.x_m = dot[0]
                self.y_m = dot[1]
                self.dot.set_data(self.x_m, self.y_m)
                self.dot.set_color(color)
                self.figure.canvas.restore_region(self.background)
                self.dot.axes.draw_artist(self.dot)
                self.figure.canvas.blit(self.dot.axes.bbox)
            except (ValueError, TypeError):
                self.x_m = event.xdata
                self.y_m = event.ydata
                self._checkDot()
                self.dot.set_data([], [])
                self.dot.axes.draw_artist(self.dot)
                self.dot.set_animated(False)
                self.background = None

    def onRelease(self, event):
        """Set the magnetic dot if somewhere near the grid ON RELEASE."""
        if event.inaxes:
            try:
                dot, _ = self.vicinity(event.xdata, event.ydata)
            except TypeError:
                # no vicinity at all
                self.x_r = event.xdata
                self.y_r = event.ydata
                self._checkDot()
                self.dot.set_data([], [])
            else:
                # if dot is not None:
                self.x_r = dot[0]
                self.y_r = dot[1]
                self._checkDot()
                self.dot.set_data([], [])
                self.dot.axes.draw_artist(self.dot)
                self.dot.set_animated(False)
                self.background = None
                self.figure.canvas.draw()

    def transform(self, x, y):
        """Transform the given x-y-coordinates to pixel position."""
        return self.figure.axis.transData.transform((x, y))

    def vicinity(self, x, y, picker=10):
        """
        Calculate the distance between a set magnet and the clicked position.

        Parameters
        ----------
        x: float
            The x-position of the current mouse event
        y: float
            The y-position of the current mouse event
        picker: int [10]
            Sets the sensitive distance to snap from

        Returns
        -------
        tuple()
            A tuple holding the cartesian x,y-coordinates of the point that will be snapped to
        """
        # pixel holds the current cursor postion
        pixel = tuple(self.transform(x, y))
        # crossings are all possible positions of grid lines
        for pos in self.crossings:
            dist_x = abs(pos[0] - pixel[0])
            dist_y = abs(pos[1] - pixel[1])
            color = '#ff0000'

            if dist_x <= picker and dist_y <= picker:
                self.parent.statusbar.showMessage("Locked X-Y-Axes", 1000)
                dot_x = pos[0]
                dot_y = pos[1]
                color = '#61ff00'

            # NOTE: 1 <= dist <= picker allows a 5 pixel radius around each
            # joint so that the junctions can be reached better
            elif 1 <= dist_x <= picker and dist_y > picker:
                self.parent.statusbar.showMessage("Locked X-Axis", 1000)
                dot_x = pos[0]
                dot_y = pixel[1]

            elif 1 <= dist_y <= picker and dist_x > picker:
                self.parent.statusbar.showMessage("Locked Y-Axis", 1000)
                dot_x = pixel[0]
                dot_y = pos[1]

            if 'dot_x' and 'dot_y' in locals():
                return self.figure.axis.transData.inverted().transform((dot_x, dot_y)), color

    def _checkDot(self):
        """
        TODO: why suddenly a list?!
        HACK: pretty dirty.. but works for now
        """
        if isinstance(self.dot, list):
            self.dot = self.dot[0]


if __name__ == '__main__':
    pass
