#!/usr/bin/env python
# encoding: UTF-8

import numpy as np


class MagnetizePolygons():
    """
    Provide the visualization of the list with nodes to magnetize and take care
    that the click-sensitive area will return the correct value to the
    magnetized coordinate.
    """

    def __init__(self, parent, x, y):
        """
        Initialize all important variables for matplotlib drawing.

        Parameters
        ----------
        parent: :meth:`core.builder.Builder`
        x: list
            The x-positions of the polygons
        y: list
            The y-positions of the polygons
        """
        print(parent)
        self.figure = parent.figure
        self.span = parent.span
        self.x = x
        self.y = y
        # the dummy dot to be magnetized and colored later
        line, = self.figure.axis.plot([], [], 'o', c='#ff0000')
        self.line = line
        self.background = None

        self.plotMagnets()

    def connect(self):
        """Connect to all the events needed."""
        self.cid_p = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def disconnect(self):
        """Disconnect all the stored connection ids."""
        self.sc.remove()
        self.figure.canvas.draw()
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    def plotMagnets(self, x=None, y=None):
        """
        Overlay the nodes as green magnets that will catch the click if in the
        defined vicinity.

        Parameters
        ----------
        x: list [None]
            x-positions of passed attribute after call from :meth:`~core.Builder.drawPoly`
        y: list [None]
            y-positions of passed attribute after call from :meth:`~core.Builder.drawPoly`
        """
        if x is None:
            x = self.x
            y = self.y
        # TODO: adjustable size and maybe color for better visibility if
        # background is shitty... settings feature
        self.sc, = self.figure.axis.plot(x, y, 'o', c='#61ff00', alpha=0.7, zorder=10)
        self.figure.canvas.draw()
        # magnetized nodes as pixel positions to get a pixel width distance --> vicinity
        self.pixelData = [tuple(self.figure.axis.transData.transform((x[i], y[i]))) for i in range(len(x))]

    def onPress(self, event):
        """Only needed for the process of creating the which-ever-polygon."""
        try:
            dot = self.vicinity(event.xdata, event.ydata)
            if dot is not None:
                self.x_p = dot[0]
                self.y_p = dot[1]
            else:
                self.x_p = None
                self.y_p = None
        except (ValueError, TypeError):
            pass

    def onMotion(self, event):
        """Color the dot within the picker distance (:meth:`vicinity`) red."""
        self.line.set_animated(True)
        self.figure.canvas.draw()
        self.background = self.figure.canvas.copy_from_bbox(self.line.axes.bbox)
        self.line.axes.draw_artist(self.line)
        self.figure.canvas.blit(self.line.axes.bbox)
        try:
            dot = self.vicinity(event.xdata, event.ydata)
            self.x_m = dot[0]
            self.y_m = dot[1]
            self.line.set_data(self.x_m, self.y_m)
            self.figure.canvas.restore_region(self.background)
            self.line.axes.draw_artist(self.line)
            self.figure.canvas.blit(self.line.axes.bbox)
        except (ValueError, TypeError):
            self.line.set_data([], [])
            self.line.axes.draw_artist(self.line)
            self.line.set_animated(False)
            self.background = None

    def onRelease(self, event):
        """Connect to the reached node if within picker distance (:meth:`vicinity`)."""
        try:
            dot = self.vicinity(event.xdata, event.ydata)
            if dot is not None:
                self.x_r = dot[0]
                self.y_r = dot[1]
            else:
                self.x_r = None
                self.y_r = None
        except (ValueError, TypeError):
            pass

    def vicinity(self, x, y, picker=15):
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
        '': tuple
            A tuple holding the cartesian x,y-coordinates of the point that will be snapped to
        """
        pixel = tuple(self.figure.axis.transData.transform((x, y)))
        for pos in self.pixelData:
            # distance:
            dist = np.sqrt((pos[0] - pixel[0])**2 + (pos[1] - pixel[1])**2)
            if dist <= picker:  # to say if it IS in the vicinity of a node
                return self.figure.axis.transData.inverted().transform(pos)


if __name__ == '__main__':
    pass
