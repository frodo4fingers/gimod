#!/usr/bin/env python
# encoding: UTF-8

import numpy as np


class MagnetizePolygons():
    """
        this class provides the graphical visualization of the list with dots to magnetize
        and takes care that the click-sensitive area will return the correct value to
        the magnetized coordinate. this will help to create polygons directly to one another.
    """

    def __init__(self, parent, x, y):
        self.figure = parent.figure
        self.span = parent.span
        self.statusBar = parent.statusbar
        self.x = x
        self.y = y
        line, = self.figure.axis.plot([0], [0], 'o', c='#ff0000')
        self.line = line
        self.background = None

        self.plotMagnets()

    def connect(self):
        self.cidP = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cidM = self.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cidR = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def disconnect(self):
        self.sc.remove()
        self.figure.canvas.draw()
        self.figure.canvas.mpl_disconnect(self.cidP)
        self.figure.canvas.mpl_disconnect(self.cidM)
        self.figure.canvas.mpl_disconnect(self.cidR)

    def plotMagnets(self, x=None, y=None):
        """
            overlays the nodes as green magnets that will catch the click
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

    def onMotion(self, event):
        self.line.set_animated(True)
        self.figure.canvas.draw()
        self.background = self.figure.canvas.copy_from_bbox(self.line.axes.bbox)
        self.line.axes.draw_artist(self.line)
        self.figure.canvas.blit(self.line.axes.bbox)
        try:
            dot = self.vicinity(event.xdata, event.ydata)
            self.xM = dot[0]
            self.yM = dot[1]
            self.line.set_data(self.xM, self.yM)
            self.figure.canvas.restore_region(self.background)
            self.line.axes.draw_artist(self.line)
            self.figure.canvas.blit(self.line.axes.bbox)
        except (ValueError, TypeError):
            self.line.set_data([0], [0])
            self.line.axes.draw_artist(self.line)
            self.line.set_animated(False)
            self.background = None

    def onPress(self, event):
        try:
            dot = self.vicinity(event.xdata, event.ydata)
            if dot is not None:
                self.xP = dot[0]
                self.yP = dot[1]
            else:
                self.xP = None
                self.yP = None
        except (ValueError, TypeError):
            pass

    def onRelease(self, event):
        try:
            dot = self.vicinity(event.xdata, event.ydata)
            if dot is not None:
                self.xR = dot[0]
                self.yR = dot[1]
            else:
                self.xR = None
                self.yR = None
        except (ValueError, TypeError):
            pass

    def vicinity(self, x, y, picker=10):
        pixel = tuple(self.figure.axis.transData.transform((x, y)))
        for pos in self.pixelData:
            # distance:
            dist = np.sqrt((pos[0] - pixel[0])**2 + (pos[1] - pixel[1])**2)
            if dist <= picker:  # to say if it IS in the vicinity of a node
                return self.figure.axis.transData.inverted().transform(pos)
